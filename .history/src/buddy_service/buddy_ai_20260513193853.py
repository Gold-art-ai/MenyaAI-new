from .voice_engine import VoiceEngine

class BuddyAI:
    def __init__(self):
        self.voice = VoiceEngine()

    def give_praise(self, student_name, precision):
        if precision > 0.8:
            # 1. Speak in Kinyarwanda first (Trust)
            rw_text = f"Yego {student_name}! Wabikoze neza cyane."
            self.voice.speak(rw_text, "RW")
            
            # 2. Bridge to English (Learning)
            en_text = "That was great! You are a star!"
            self.voice.speak(en_text, "EN")
        else:
            self.voice.speak("Gerageza rimwe gusa, urabishobora!", "RW")
            self.voice.speak("Try one more time!", "EN")