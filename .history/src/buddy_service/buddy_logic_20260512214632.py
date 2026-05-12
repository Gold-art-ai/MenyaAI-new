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

    def get_buddy_response(self, precision, language="RW"):
        """Selects a response based on the precision score."""
        # Logic: If precision is above 0.7, it's a success. Otherwise, encouragement.
        category = "success" if precision >= 0.7 else "encourage"
        
        # Pick a random phrase from the selected language and category
        options = self.phrases[category].get(language, self.phrases[category]["EN"])
        return random.choice(options)