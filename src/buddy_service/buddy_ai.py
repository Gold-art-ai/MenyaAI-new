import urllib.request
import json
import os
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
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

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

    def _call_gemini(self, system_prompt, user_prompt):
        """Calls the Gemini 2.5 Flash API via direct HTTP request to avoid external package requirements."""
        if not self.gemini_api_key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_prompt}\n\n{user_prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 60
            }
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if text:
                        return text
        except Exception as e:
            print(f"\n [BuddyAI Warning] Gemini API call failed: {e}")
        return None

    def _call_ollama(self, system_prompt, user_prompt):
        """Calls the local Ollama SLM endpoint if available."""
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 60
            }
        }
        try:
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
        return None

    def generate_response(self, student_name, precision, current_act, next_task, language_preference="RW-EN", jerk_index=0.0, velocity_variance=0.0):
        """
        Generates feedback using Gemini API (if key present), local Ollama, or rules-based fallback.
        Incorporates tremor (jerk) and speed metrics for highly targeted pediatric motor support.
        """
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")

        system_prompt = (
            "You are an enthusiastic cartoon character buddy teacher speaking to a toddler (under 5 years old). "
            "Speak in a very simple, encouraging, friendly tone. "
            "Only talk about the drawing/writing activity and motor control. "
            "Keep sentences extremely short (max 12 words total)."
        )

        # Base user prompt details
        user_prompt = (
            f"The toddler {student_name} just drew {curr_en} with {int(precision * 100)}% accuracy. "
        )

        # Dynamic kinematic insights in prompt
        if jerk_index > 5.0:
            user_prompt += "The child's hand was shaking/trembling quite a bit. Gently advice them to draw slowly and steady. "
        elif precision < 0.6:
            user_prompt += "The child had difficulty following the path. Give simple, positive encouragement to try again. "
        else:
            user_prompt += "The child drew beautifully and smoothly! Praise their progress. "

        if language_preference == "RW-EN":
            user_prompt += (
                f"The next activity is {next_en}. "
                "You must start in Kinyarwanda using [RW] tag, then switch to English using [EN] tag. "
                "Example: [RW] Wabikoze neza cyane! [EN] Let's try drawing shapes next!"
            )
        elif language_preference == "RW-FR":
            user_prompt += (
                f"The next activity is {next_fr}. "
                "You must start in Kinyarwanda using [RW] tag, then switch to French using [FR] tag. "
                "Example: [RW] Wabikoze neza cyane! [FR] Dessinons un carré !"
            )
        elif language_preference == "RW":
            user_prompt += f"Write the entire response only in Kinyarwanda using [RW] tag, talking about {curr_rw} and {next_rw}."
        elif language_preference == "FR":
            user_prompt += f"Write the entire response only in French using [FR] tag, talking about {curr_fr} and {next_fr}."
        else:
            user_prompt += f"Write the entire response only in English using [EN] tag, talking about {curr_en} and {next_en}."

        # 1. Try Gemini API first (if key configured)
        if self.gemini_api_key:
            res = self._call_gemini(system_prompt, user_prompt)
            if res:
                return res

        # 2. Try Local Ollama
        res = self._call_ollama(system_prompt, user_prompt)
        if res:
            return res

        # 3. Fallback to rule-based templates
        return self._generate_fallback(student_name, precision, current_act, next_task, language_preference, jerk_index)

    def _generate_fallback(self, student_name, precision, current_act, next_task, language_preference, jerk_index=0.0):
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")

        # Tremor-specific fallback advice
        if jerk_index > 5.0:
            if language_preference == "RW-EN":
                return f"[RW] Komeza buhoro buhoro {student_name}, urabishobora! [EN] Draw slowly and steady!"
            elif language_preference == "RW-FR":
                return f"[RW] Komeza buhoro buhoro {student_name}, urabishobora! [FR] Dessine lentement et calmement !"
            elif language_preference == "RW":
                return f"[RW] Komeza buhoro buhoro {student_name}, shyira ikaramu hasi buhoro!"
            elif language_preference == "FR":
                return f"[FR] Doucement, {student_name} ! Dessine lentement et calmement !"
            else:
                return f"[EN] Draw slowly and steady, {student_name}! You can do it!"

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

    def give_praise(self, student_name, precision, current_act, next_task, language_preference="RW-EN", jerk_index=0.0, velocity_variance=0.0):
        response_text = self.generate_response(student_name, precision, current_act, next_task, language_preference, jerk_index, velocity_variance)
        print(f"\n [BUDDY RESPONSE]: {response_text}")
        self.voice.speak(response_text)

