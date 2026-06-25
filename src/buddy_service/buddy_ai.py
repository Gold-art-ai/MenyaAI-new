import urllib.request
import json
import os
import random
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

# Cartoon phrase pools for randomized conversational offline fallback
INTRO_CARTOON = {
    "RW": ["Yego kabisa!", "Wawu!", "Urakoze cyane!", "Bip-bop, reba!", "Agasaro!", "Yego!", "Wabikoze!"],
    "EN": ["Woohoo!", "Oh wow!", "Beep-boop!", "Awesome!", "High five!", "Yippee!", "Yay!"],
    "FR": ["Youpi !", "Oh là là !", "Bip-bop !", "Super !", "Génial !", "Gagné !", "Bravo !"]
}

PRAISE_PHRASES = {
    "RW": ["Wabikoze neza cyane!", "Uri umuhanga!", "Njyewe ndagukunda!", "Ni byiza cyane!", "Uri igitangaza!", "Ukoze neza cyane!"],
    "EN": ["Great job!", "You are a star!", "I'm so proud of you!", "Incredible tracing!", "Perfect shape!", "Amazing progress!"],
    "FR": ["C'est magnifique !", "Tu es un génie !", "Je suis fier de toi !", "Superbe !", "Excellent dessin !", "Quel progrès !"]
}

ENCOURAGE_PHRASES = {
    "RW": ["Gerageza bwa kabiri, urabishobora!", "Komeza ushushanye!", "Ntucike intege!", "Biraza kuza buhoro buhoro!", "Shyiramo ingufu, uri hafi!"],
    "EN": ["Try again, you can do it!", "Keep drawing!", "Don't give up!", "You're almost there!", "Let's try one more time!"],
    "FR": ["Réessaie, tu peux le faire !", "Continue de dessiner !", "N'abandonne pas !", "Tu y es presque !", "Réessaye encore une fois !"]
}

TREMOR_PHRASES = {
    "RW": ["Komeza buhoro buhoro, urembereze ikaramu neza!", "Shyira ikaramu hasi buhoro, tura utuje!", "Buhoro buhoro urabishobora!", "Komeza witonde buhoro buhoro!"],
    "EN": ["Draw slowly and steady!", "Take a breath, slow and steady!", "Let's draw very slowly, it is easier!", "Steady hand, slow and easy!"],
    "FR": ["Dessine lentement et calmement !", "Prends ton temps, doucement !", "Dessine doucement, c'est plus facile !", "Maintiens la main stable et avance doucement !"]
}

class BuddyAI:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="phi3", rw_voice="sw-KE-ZuriNeural", state_file="data/student_state.json"):
        self.voice = VoiceEngine(rw_voice=rw_voice)
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.state_file = state_file
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_state(self, state):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=4)
        except Exception:
            pass

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

    def _call_openai(self, system_prompt, user_prompt, chat_history_list):
        """Calls the OpenAI API via direct HTTP request to avoid external package requirements."""
        if not self.openai_api_key:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        
        # Build conversational messages context natively
        messages = [{"role": "system", "content": system_prompt}]
        for role, content in chat_history_list:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_prompt})
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 60,
            "temperature": 0.7
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                choices = res_data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "").strip()
                    if text:
                        return text
        except Exception as e:
            print(f"\n [BuddyAI Warning] OpenAI API call failed: {e}")
        return None

    def _call_gemini(self, system_prompt, user_prompt):
        """Calls the Gemini 2.5 Flash API via direct HTTP request."""
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
        Generates stateful conversational feedback using OpenAI, Gemini, local Ollama, or rich fallback templates.
        Integrates session chat history to make responses highly contextual and engaging.
        """
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")

        # 1. Load Chat Memory
        state = self._load_state()
        if student_name not in state:
            state[student_name] = {}
        if "chat_history" not in state[student_name]:
            state[student_name]["chat_history"] = []
            
        chat_history_list = state[student_name]["chat_history"][-4:]  # Context of last 4 turns (2 exchanges)

        system_prompt = (
            "You are an enthusiastic talking cartoon character buddy teacher speaking to a toddler (under 5 years old). "
            "Speak in a very simple, encouraging, friendly tone. "
            "Avoid static templates; sound like a real chatting conversation! "
            "Only talk about the drawing/writing activity and motor control. "
            "Keep sentences extremely short (max 12 words total)."
        )

        # Base user prompt details
        user_prompt = (
            f"The toddler {student_name} just drew {curr_en} with {int(precision * 100)}% accuracy. "
        )

        if jerk_index > 5.0:
            user_prompt += "The child's hand was shaking. Gently advice them to draw slowly and steady. "
        elif precision < 0.6:
            user_prompt += "The child struggled a bit. Give simple, positive encouragement. "
        else:
            user_prompt += "The child drew beautifully and smoothly! Praise their progress. "

        # Format historical context for LLMs that only take single string prompts (Gemini, Ollama)
        history_context = ""
        if chat_history_list:
            history_context = "\n\nHere is our recent chat history for context (do not repeat your past statements):\n"
            for role, content in chat_history_list:
                name = "Buddy" if role == "assistant" else "Student Performance"
                history_context += f"- {name}: {content}\n"

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

        response_text = None

        # 1. Try OpenAI Chat API (Highly conversational)
        if self.openai_api_key:
            response_text = self._call_openai(system_prompt, user_prompt, chat_history_list)

        # 2. Try Gemini API
        if not response_text and self.gemini_api_key:
            response_text = self._call_gemini(system_prompt, f"{user_prompt}{history_context}")

        # 3. Try Local Ollama
        if not response_text:
            response_text = self._call_ollama(system_prompt, f"{user_prompt}{history_context}")

        # 4. Fallback to rich rule-based templates if all APIs fail
        if not response_text:
            response_text = self._generate_fallback(student_name, precision, current_act, next_task, language_preference, jerk_index)

        # Update and save chat history in student state
        student_summary = f"Drew {curr_en} with {int(precision * 100)}% accuracy. Jerk: {jerk_index:.1f}."
        chat_history_list.append(("user", student_summary))
        chat_history_list.append(("assistant", response_text))
        
        # Keep last 10 entries
        if len(chat_history_list) > 10:
            chat_history_list = chat_history_list[-10:]
            
        state[student_name]["chat_history"] = chat_history_list
        self._save_state(state)

        return response_text

    def _generate_fallback(self, student_name, precision, current_act, next_task, language_preference, jerk_index=0.0):
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")

        # Select randomized phrases to prevent static repetition
        intro_rw = random.choice(INTRO_CARTOON["RW"])
        intro_en = random.choice(INTRO_CARTOON["EN"])
        intro_fr = random.choice(INTRO_CARTOON["FR"])

        # Tremor-specific fallback advice
        if jerk_index > 5.0:
            tremor_rw = random.choice(TREMOR_PHRASES["RW"])
            tremor_en = random.choice(TREMOR_PHRASES["EN"])
            tremor_fr = random.choice(TREMOR_PHRASES["FR"])
            
            if language_preference == "RW-EN":
                return f"[RW] {intro_rw} {tremor_rw} [EN] {tremor_en}"
            elif language_preference == "RW-FR":
                return f"[RW] {intro_rw} {tremor_rw} [FR] {tremor_fr}"
            elif language_preference == "RW":
                return f"[RW] {intro_rw} {tremor_rw}"
            elif language_preference == "FR":
                return f"[FR] {intro_fr} {tremor_fr}"
            else:
                return f"[EN] {intro_en} {tremor_en}"

        if precision >= 0.7:
            praise_rw = random.choice(PRAISE_PHRASES["RW"])
            praise_en = random.choice(PRAISE_PHRASES["EN"])
            praise_fr = random.choice(PRAISE_PHRASES["FR"])
            
            if language_preference == "RW-EN":
                return f"[RW] {intro_rw} {praise_rw} kuri {curr_rw}! [EN] {praise_en} Let's try {next_en} next!"
            elif language_preference == "RW-FR":
                return f"[RW] {intro_rw} {praise_rw} kuri {curr_rw}! [FR] {praise_fr} Essayons de faire {next_fr} !"
            elif language_preference == "RW":
                return f"[RW] {intro_rw} {praise_rw} Reka tugerageze {next_rw}!"
            elif language_preference == "FR":
                return f"[FR] {intro_fr} {praise_fr} Apprenons à faire {next_fr} !"
            else:
                return f"[EN] {intro_en} {praise_en} Let's learn to do {next_en}!"
        else:
            enc_rw = random.choice(ENCOURAGE_PHRASES["RW"])
            enc_en = random.choice(ENCOURAGE_PHRASES["EN"])
            enc_fr = random.choice(ENCOURAGE_PHRASES["FR"])
            
            if language_preference == "RW-EN":
                return f"[RW] {intro_rw} {enc_rw} kuri {curr_rw}! [EN] {enc_en}"
            elif language_preference == "RW-FR":
                return f"[RW] {intro_rw} {enc_rw} kuri {curr_rw}! [FR] {enc_fr}"
            elif language_preference == "RW":
                return f"[RW] {intro_rw} {enc_rw}"
            elif language_preference == "FR":
                return f"[FR] {intro_fr} {enc_fr}"
            else:
                return f"[EN] {intro_en} {enc_en}"

    def give_praise(self, student_name, precision, current_act, next_task, language_preference="RW-EN", jerk_index=0.0, velocity_variance=0.0):
        response_text = self.generate_response(student_name, precision, current_act, next_task, language_preference, jerk_index, velocity_variance)
        print(f"\n [BUDDY RESPONSE]: {response_text}")
        self.voice.speak(response_text)

