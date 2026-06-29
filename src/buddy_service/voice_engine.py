import asyncio
import edge_tts
import tempfile
import os
import ctypes
import pyttsx3
import re
import hashlib

# ─────────────────────────────────────────────────────────────────────────────
# KINYARWANDA PHONEME PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

WORD_OVERRIDES = {
    # Keep overrides minimal since Latin vowels (a, e, i, o, u) share identical values in Swahili and Kinyarwanda
}

RW_PHONEME_RULES = [
    # ── Palatalization & consonants ──────────────────────────────────────────
    ("cy", "ch"),   # cyane -> chane, icyatsi -> ichatsi
    ("jy", "j"),    # jye -> je, ujye -> uje
    ("shy", "sh"),  # shyira -> shira, inshuti -> inshuti (Swahili sh)

    # Standard "c" (without y) -> "ch" (since Swahili always writes ch for [tʃ])
    ("ca", "cha"),  ("ce", "che"),  ("ci", "chi"),  ("co", "cho"),  ("cu", "chu"),

    # ── Vowel length collapse (fallback for double vowels) ───────────────────
    ("aa", "a"), ("ee", "e"), ("ii", "i"), ("oo", "o"), ("uu", "u"),
]


def preprocess_kinyarwanda(text: str) -> str:
    """
    Two-pass preprocessor:
      Pass 1 — whole-word overrides (most accurate, checked first)
      Pass 2 — phoneme rules applied left to right in order
    """
    words = text.lower().split()
    words = [WORD_OVERRIDES.get(w, w) for w in words]
    text = " ".join(words)

    for rw_pattern, approximation in RW_PHONEME_RULES:
        text = text.replace(rw_pattern, approximation)

    return text


# ─────────────────────────────────────────────────────────────────────────────
# VOICE ENGINE
# ─────────────────────────────────────────────────────────────────────────────

# Warm, expressive Edge TTS voice for English — child-friendly (free)
EN_VOICE = "en-US-AriaNeural"

class VoiceEngine:
    def __init__(self, rw_voice="sw-KE-ZuriNeural"):
        self.rw_voice = rw_voice
        self.en_engine = None   # pyttsx3 — lazy, only used as offline fallback
        self.cache_dir = "data/tts_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_pyttsx3_fallback(self):
        """Returns a pyttsx3 engine — only used when Edge TTS has no internet."""
        if self.en_engine is None:
            self.en_engine = pyttsx3.init()
            self.en_engine.setProperty('rate', 150)
        return self.en_engine

    def _play_native_windows(self, file_path):
        """Plays an MP3 directly through Windows MCI — no external player opens."""
        import uuid
        alias = f"my_audio_{uuid.uuid4().hex[:8]}"
        mci = ctypes.windll.winmm
        
        # Open the audio file with a unique alias
        open_cmd = f'open "{file_path}" type mpegvideo alias {alias}'
        ret_open = mci.mciSendStringW(open_cmd, None, 0, 0)
        if ret_open != 0:
            err_buf = ctypes.create_unicode_buffer(256)
            mci.mciGetErrorStringW(ret_open, err_buf, 256)
            print(f"\n[VoiceEngine Error] Failed to open audio device (MCI Error {ret_open}: {err_buf.value})")
            return

        try:
            # Play the audio and wait for it to complete
            ret_play = mci.mciSendStringW(f'play {alias} wait', None, 0, 0)
            if ret_play != 0:
                err_buf = ctypes.create_unicode_buffer(256)
                mci.mciGetErrorStringW(ret_play, err_buf, 256)
                print(f"\n[VoiceEngine Error] Failed to play audio (MCI Error {ret_play}: {err_buf.value})")
        finally:
            # Always close the MCI alias to release the device and file locks
            mci.mciSendStringW(f'close {alias}', None, 0, 0)

    async def _generate_tts_file(self, text: str, voice: str, target_path: str) -> str:
        """Generate TTS audio and save to target path."""
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(target_path)
        return target_path

    def _parse_segments(self, text, default_lang="RW"):
        """Parse tagged text into a list of (text, lang_code) tuples."""
        segments = re.split(r'(\[[A-Z]{2}\])', text)
        if len(segments) <= 1:
            return [(text.strip(), default_lang)] if text.strip() else []

        result = []
        current_lang = default_lang
        for seg in segments:
            if not seg:
                continue
            if seg.startswith('[') and seg.endswith(']'):
                current_lang = seg[1:-1]
            else:
                cleaned = seg.strip()
                if cleaned:
                    result.append((cleaned, current_lang))
        return result

    async def _pregenerate_all_tts(self, tts_tasks):
        """
        Pre-generate all Edge TTS audio files concurrently.
        tts_tasks: list of (index, text, voice, target_path) tuples
        Returns: dict mapping index -> target_file_path
        """
        async def _gen(idx, text, voice, target_path):
            path = await self._generate_tts_file(text, voice, target_path)
            return (idx, path)

        results = await asyncio.gather(*[_gen(i, t, v, p) for i, t, v, p in tts_tasks])
        return dict(results)

    def speak(self, text, lang_code="RW"):
        """
        Main entry point. Supports inline language tags: [RW], [EN], [FR]

        FAST mode: all Edge TTS segments are generated concurrently (parallel
        network requests), then played back sequentially with no wait between them.

        Examples:
            engine.speak("Muraho neza")
            engine.speak("[RW] Muraho [EN] Hello [FR] Bonjour")
        """
        parsed = self._parse_segments(text, default_lang=lang_code)
        if not parsed:
            return

        # Collect Edge TTS tasks for ALL languages (RW, FR, EN) concurrently
        tts_tasks = []  # (index, processed_text, voice, target_path)
        tts_files = {}  # index -> target_file_path

        for i, (seg_text, seg_lang) in enumerate(parsed):
            if seg_lang in ("RW", "FR", "EN"):
                if seg_lang == "RW":
                    voice = self.rw_voice
                    processed_text = preprocess_kinyarwanda(seg_text)
                elif seg_lang == "FR":
                    voice = "fr-FR-DeniseNeural"
                    processed_text = seg_text
                else:  # EN — warm Aria voice instead of robotic pyttsx3
                    voice = EN_VOICE
                    processed_text = seg_text

                # Check persistent cache first
                text_hash = hashlib.md5(f"{processed_text}_{voice}".encode("utf-8")).hexdigest()
                cached_path = os.path.join(self.cache_dir, f"{text_hash}.mp3")

                if os.path.exists(cached_path) and os.path.getsize(cached_path) > 0:
                    tts_files[i] = cached_path
                else:
                    tts_tasks.append((i, processed_text, voice, cached_path))

        # Pre-generate all missing TTS audio concurrently (one network round-trip)
        if tts_tasks:
            try:
                new_files = asyncio.run(self._pregenerate_all_tts(tts_tasks))
                tts_files.update(new_files)
            except Exception as e:
                print(f"\n[VoiceEngine] Edge TTS unavailable ({e}), falling back to pyttsx3 for EN.")

        # Play back all segments in order
        for i, (seg_text, seg_lang) in enumerate(parsed):
            if i in tts_files:
                self._play_native_windows(tts_files[i])
            elif seg_lang == "EN":
                # Offline fallback: pyttsx3 (only when Edge TTS has no internet)
                engine = self._get_pyttsx3_fallback()
                engine.say(seg_text)
                engine.runAndWait()