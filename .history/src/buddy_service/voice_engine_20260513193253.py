import asyncio
import edge_tts
import tempfile
import os
import ctypes
import pyttsx3

class VoiceEngine:
    def __init__(self):
        # Initialize the English offline engine
        self.en_engine = pyttsx3.init()
        self.en_engine.setProperty('rate', 150)
        
    def _play_native_windows(self, file_path):
        """Plays audio directly through Windows MCI without opening external players."""
        mci = ctypes.windll.winmm
        mci.mciSendStringW(f'open "{file_path}" type mpegvideo alias my_audio', None, 0, 0)
        mci.mciSendStringW('play my_audio wait', None, 0, 0)
        mci.mciSendStringW('close my_audio', None, 0, 0)

    async def _generate_and_play_rw(self, text):
        """Uses Edge-TTS (Rafiki) for Kinyarwanda/Swahili phonetic reading."""
        communicate = edge_tts.Communicate(text, voice="sw-KE-RafikiNeural")
        
        # Create a temp file that deletes itself after use
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            temp_path = tmp.name
            
        await communicate.save(temp_path)
        try:
            self._play_native_windows(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def speak(self, text, lang_code="RW"):
        """The main entry point for the Buddy to talk."""
        if lang_code == "EN":
            self.en_engine.say(text)
            self.en_engine.runAndWait()
        
        elif lang_code == "RW":
            # Run the async Kinyarwanda function
            asyncio.run(self._generate_and_play_rw(text))
            
        elif lang_code == "FR":
            # You can add French here later using edge_tts voice="fr-FR-DeniseNeural"
            asyncio.run(self._generate_and_play_rw(text))
            