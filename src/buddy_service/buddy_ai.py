import urllib.request
import json
from .voice_engine import VoiceEngine

# Kid-friendly descriptors for the technical activity levels
ACTIVITY_DESCRIPTIONS = {
    "Lines": {
        "EN": "tracing lines",
        "RW": "gushushanya imirongo",
        "FR": "tracer des lignes"
    },
    "Lines_Review": {
        "EN": "practicing lines again",
        "RW": "gusubira ku mirongo",
        "FR": "s'entraîner sur les lignes"
    },
    "Shapes": {
        "EN": "drawing shapes",
        "RW": "gushushanya ishusho",
        "FR": "dessiner des formes"
    },
    "Shapes_Review": {
        "EN": "practicing shapes again",
        "RW": "gusubira ku ishusho",
        "FR": "s'entraîner sur les formes"
    },
    "Letters": {
        "EN": "writing letters",
        "RW": "gushushanya inyuguti",
        "FR": "écrire des lettres"
    },
    "Letters_Review": {
        "EN": "practicing letters again",
        "RW": "gusubira ku nyuguti",
        "FR": "s'entraîner sur les lettres"
    },
    "Numbers": {
        "EN": "tracing numbers",
        "RW": "gushushanya imibare",
        "FR": "tracer des chiffres"
    },
    "Numbers_Review": {
        "EN": "practicing numbers again",
        "RW": "gusubira ku mibare",
        "FR": "s'entraîner sur les chiffres"
    },
    "Words": {
        "EN": "writing words",
        "RW": "kwandika amagambo",
        "FR": "écrire des mots"
    },
    "Words_Review": {
        "EN": "practicing words again",
        "RW": "gusubira ku magambo",
        "FR": "s'entraîner sur les mots"
    },
    "MathBasics": {
        "EN": "doing simple math",
        "RW": "gukora imibare y'ibanze",
        "FR": "faire des calculs simples"
    },
    "MathBasics_Review": {
        "EN": "practicing math again",
        "RW": "gusubira ku mibare y'ibanze",
        "FR": "s'entraîner sur les calculs"
    },
    "ReadSimple": {
        "EN": "reading simple words",
        "RW": "gusoma amagambo yoroshye",
        "FR": "lire des mots simples"
    },
    "ReadSimple_Review": {
        "EN": "practicing reading again",
        "RW": "gusubira ku gusoma",
        "FR": "s'entraîner sur la lecture"
    }
}

class BuddyAI:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="phi3", rw_voice="sw-KE-ZuriNeural"):
        self.voice = VoiceEngine(rw_voice=rw_voice)
        self.ollama_url = ollama_url
        self.model_name = model_name

    def _get_act_desc(self, activity, lang):
        """Translates technical activity labels to toddler-friendly language descriptions."""
        activity = str(activity).strip()
        default_desc = {
            "EN": activity.lower().replace("_", " "),
            "RW": activity.lower().replace("_", " "),
            "FR": activity.lower().replace("_", " ")
        }
        desc = ACTIVITY_DESCRIPTIONS.get(activity, default_desc)
        return desc.get(lang, desc["EN"])

    def generate_response(self, student_name, precision, current_act, next_task, language_preference="RW-EN"):
        """
        Generates feedback using Ollama SLM if available, otherwise falls back to a rules-based template.
        """
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")

        system_prompt = (
            "You are an enthusiastic cartoon buddy teacher talking to a toddler. "
            "Speak in a very simple, encouraging, friendly tone. "
            "Only talk about the current drawing activity and learning. Never say anything else. "
            "Keep sentences extremely short (max 15 words total). "
        )

        user_prompt = (
            f"The toddler {student_name} just drew {curr_en} with {int(precision * 100)}% accuracy. "
        )

        if language_preference == "RW-EN":
            user_prompt += (
                f"The next activity is {next_en}. "
                "Format the response so you start in Kinyarwanda using [RW] tag to build trust, then switch to English using [EN] tag. "
                "Example: [RW] Wabikoze neza! [EN] Great job! Today we are learning circles!"
            )
        elif language_preference == "RW-FR":
            user_prompt += (
                f"The next activity is {next_fr}. "
                "Format the response so you start in Kinyarwanda using [RW] tag to build trust, then switch to French using [FR] tag. "
                "Example: [RW] Wabikoze neza! [FR] C'est magnifique! Dessinons un carré!"
            )
        elif language_preference == "RW":
            user_prompt += f"Write the entire response only in Kinyarwanda using [RW] tag, talking about {curr_rw} and {next_rw}."
        elif language_preference == "FR":
            user_prompt += f"Write the entire response only in French using [FR] tag, talking about {curr_fr} and {next_fr}."
        else:
            user_prompt += f"Write the entire response only in English using [EN] tag, talking about {curr_en} and {next_en}."

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
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")

        if precision >= 0.7:
            if language_preference == "RW-EN":
                return f"[RW] Yego {student_name}! Wabikoze neza cyane kuri {curr_rw}! [EN] That was a great job! Now let's try {next_en}!"
            elif language_preference == "RW-FR":
                return f"[RW] Yego {student_name}! Wabikoze neza cyane kuri {curr_rw}! [FR] Très bon travail ! Essayons de faire {next_fr} !"
            elif language_preference == "RW":
                return f"[RW] Yego {student_name}! Wabikoze neza cyane kuri {curr_rw}! Reka tugerageze {next_rw}!"
            elif language_preference == "FR":
                return f"[FR] Excellent travail, {student_name} ! Tu as bien réussi {curr_fr} ! Apprenons à faire {next_fr} !"
            else:
                return f"[EN] Awesome job, {student_name}! You drew a perfect {curr_en}! Let's learn to do {next_en}!"
        else:
            if language_preference == "RW-EN":
                return f"[RW] Gerageza rimwe gusa {student_name}, urabishobora kuri {curr_rw}! [EN] Try one more time! You can do it!"
            elif language_preference == "RW-FR":
                return f"[RW] Gerageza rimwe gusa {student_name}, urabishobora kuri {curr_rw}! [FR] Réessaie encore une fois, tu peux le faire !"
            elif language_preference == "RW":
                return f"[RW] Komeza ugerageze {student_name}, urabishobora kuri {curr_rw}!"
            elif language_preference == "FR":
                return f"[FR] N'abandonne pas, {student_name}! Réessaie encore une fois sur {curr_fr}!"
            else:
                return f"[EN] Don't give up, {student_name}! Let's try drawing {curr_en} again!"

    def give_praise(self, student_name, precision, current_act, next_task, language_preference="RW-EN"):
        response_text = self.generate_response(student_name, precision, current_act, next_task, language_preference)
        print(f"\n [BUDDY RESPONSE]: {response_text}")
        self.voice.speak(response_text)
