import urllib.request
import json
from .voice_engine import VoiceEngine

class BuddyAI:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="phi3"):
        self.voice = VoiceEngine()
        self.ollama_url = ollama_url
        self.model_name = model_name

    def generate_response(self, student_name, precision, current_act, next_task, language_preference="RW-EN"):
        """
        Generates feedback using Ollama SLM if available, otherwise falls back to a rules-based template.
        """
        system_prompt = (
            "You are an enthusiastic cartoon buddy teacher talking to a toddler. "
            "Speak in a very simple, encouraging, friendly tone. "
            "Only talk about the current drawing activity and learning. Never say anything else. "
            "Keep sentences extremely short (max 15 words total). "
        )

        user_prompt = (
            f"The toddler {student_name} just drew {current_act} with {int(precision * 100)}% accuracy. "
            f"The next activity is {next_task}. "
        )

        if language_preference == "RW-EN":
            user_prompt += (
                "Format the response so you start in Kinyarwanda using [RW] tag to build trust, then switch to English using [EN] tag. "
                "Example: [RW] Wabikoze neza! [EN] Great job! Today we are learning circles!"
            )
        elif language_preference == "RW-FR":
            user_prompt += (
                "Format the response so you start in Kinyarwanda using [RW] tag to build trust, then switch to French using [FR] tag. "
                "Example: [RW] Wabikoze neza! [FR] C'est magnifique! Dessinons un carré!"
            )
        elif language_preference == "RW":
            user_prompt += "Write the entire response only in Kinyarwanda using [RW] tag."
        elif language_preference == "FR":
            user_prompt += "Write the entire response only in French using [FR] tag."
        else:
            user_prompt += "Write the entire response only in English using [EN] tag."

        try:
            payload = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 60
                }
            }
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                text = res_data.get("response", "").strip()
                if text:
                    return text
        except Exception:
            pass

        return self._generate_fallback(student_name, precision, current_act, next_task, language_preference)

    def _generate_fallback(self, student_name, precision, current_act, next_task, language_preference):
        if precision >= 0.7:
            if language_preference == "RW-EN":
                return f"[RW] Yego {student_name}! Wabikoze neza cyane kuri {current_act}! [EN] That was a great {current_act}! Now let's try {next_task}!"
            elif language_preference == "RW-FR":
                return f"[RW] Yego {student_name}! Wabikoze neza cyane kuri {current_act}! [FR] Très bon travail sur le {current_act}! Essayons le {next_task}!"
            elif language_preference == "RW":
                return f"[RW] Yego {student_name}! Wabikoze neza cyane kuri {current_act}! Reka tugerageze {next_task}!"
            elif language_preference == "FR":
                return f"[FR] Excellent travail, {student_name}! Tu as dessiné un {current_act} parfait! Apprenons le {next_task}!"
            else:
                return f"[EN] Awesome job, {student_name}! You drew a perfect {current_act}! Let's learn {next_task}!"
        else:
            if language_preference == "RW-EN":
                return f"[RW] Gerageza rimwe gusa {student_name}, urabishobora kuri {current_act}! [EN] Try one more time! You can do it!"
            elif language_preference == "RW-FR":
                return f"[RW] Gerageza rimwe gusa {student_name}, urabishobora kuri {current_act}! [FR] Réessaie encore une fois, tu peux le faire !"
            elif language_preference == "RW":
                return f"[RW] Komeza ugerageze {student_name}, urabishobora kuri {current_act}!"
            elif language_preference == "FR":
                return f"[FR] N'abandonne pas, {student_name}! Réessaie encore une fois sur le {current_act}!"
            else:
                return f"[EN] Don't give up, {student_name}! Let's try drawing {current_act} again!"

    def give_praise(self, student_name, precision, current_act, next_task, language_preference="RW-EN"):
        response_text = self.generate_response(student_name, precision, current_act, next_task, language_preference)
        print(f"\n [BUDDY RESPONSE]: {response_text}")
        self.voice.speak(response_text)