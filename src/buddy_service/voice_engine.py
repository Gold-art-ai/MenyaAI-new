import asyncio
import edge_tts
import tempfile
import os
import ctypes
import pyttsx3
import re

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

class VoiceEngine:
    def __init__(self, rw_voice="sw-KE-ZuriNeural"):
        self.rw_voice = rw_voice
        self.en_engine = pyttsx3.init()
        self.en_engine.setProperty('rate', 150)

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

    async def _generate_tts_file(self, text: str, voice: str) -> str:
        """Generate TTS audio to a temp MP3 file, returns the file path."""
        communicate = edge_tts.Communicate(text, voice=voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            temp_path = tmp.name
        await communicate.save(temp_path)
        return temp_path

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
        tts_tasks: list of (index, text, voice) tuples
        Returns: dict mapping index -> temp_file_path
        """
        async def _gen(idx, text, voice):
            path = await self._generate_tts_file(text, voice)
            return (idx, path)

        results = await asyncio.gather(*[_gen(i, t, v) for i, t, v in tts_tasks])
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

        # Collect Edge TTS tasks for concurrent generation
        tts_tasks = []  # (index, processed_text, voice)
        for i, (seg_text, seg_lang) in enumerate(parsed):
            if seg_lang == "RW":
                tts_tasks.append((i, preprocess_kinyarwanda(seg_text), self.rw_voice))
            elif seg_lang == "FR":
                tts_tasks.append((i, seg_text, "fr-FR-DeniseNeural"))

        # Pre-generate all TTS audio files concurrently (one network round-trip)
        tts_files = {}
        if tts_tasks:
            tts_files = asyncio.run(self._pregenerate_all_tts(tts_tasks))

        # Play back all segments in order — TTS files are already on disk
        try:
            for i, (seg_text, seg_lang) in enumerate(parsed):
                if seg_lang == "EN":
                    self.en_engine.say(seg_text)
                    self.en_engine.runAndWait()
                elif i in tts_files:
                    self._play_native_windows(tts_files[i])
        finally:
            # Clean up all temp files
            for path in tts_files.values():
                if os.path.exists(path):
                    os.remove(path)