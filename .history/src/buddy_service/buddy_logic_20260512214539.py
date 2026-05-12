import random

class BuddyService:
    def __init__(self):
        # Dictionary of phrases in 3 languages
        self.phrases = {
            "success": {
                "RW": ["Wabikoze neza cyane!", "Uri umuhanga!", "Njyewe ndagukunda!"],
                "EN": ["Great job!", "You are a star!", "I'm so proud of you!"],
                "FR": ["C'est magnifique !", "Tu es un génie !", "Je suis fier de toi !"]
            },
            "encourage": {
                "RW": ["Gerageza bwa kabiri, urabishobora!", "Komeza ushushanye!", "Ntucike intege!"],
                "EN": ["Try again, you can do it!", "Keep drawing!", "Don't give up!"],
                "FR": ["Réessaie, tu peux le faire !", "Continue de dessiner !", "N'abandonne pas !"]
            }
        }
