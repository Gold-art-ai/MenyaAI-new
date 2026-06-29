import urllib.request
import urllib.error
import json
import os
import random
import socket
import time
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOTENV_PATH = find_dotenv(usecwd=True) or str(PROJECT_ROOT / ".env")
load_dotenv(DOTENV_PATH)

# ========================== YOUR ORIGINAL PHRASES ==========================
ACTIVITY_DESCRIPTIONS = {
    "Lines": {"EN": "tracing lines", "RW": "gushushanya imirongo", "FR": "tracer des lignes"},
    "Lines_Review": {"EN": "practicing lines again", "RW": "gusubira ku mirongo", "FR": "s'entraîner sur les lignes"},
    "Shapes": {"EN": "drawing shapes", "RW": "gushushanya ishusho", "FR": "dessiner des formes"},
    "Shapes_Review": {"EN": "practicing shapes again", "RW": "gusubira ku ishusho", "FR": "s'entraîner sur les formes"},
    "Letters": {"EN": "writing letters", "RW": "gushushanya inyuguti", "FR": "écrire des lettres"},
    "Letters_Review": {"EN": "practicing letters again", "RW": "gusubira ku nyuguti", "FR": "s'entraîner sur les lettres"},
    "Numbers": {"EN": "tracing numbers", "RW": "gushushanya imibare", "FR": "tracer des chiffres"},
    "Numbers_Review": {"EN": "practicing numbers again", "RW": "gusubira ku mibare", "FR": "s'entraîner sur les chiffres"},
    "Words": {"EN": "writing words", "RW": "kwandika amagambo", "FR": "écrire des mots"},
    "Words_Review": {"EN": "practicing words again", "RW": "gusubira ku magambo", "FR": "s'entraîner sur les mots"},
    "MathBasics": {"EN": "doing simple math", "RW": "gukora imibare y'ibanze", "FR": "faire des calculs simples"},
    "MathBasics_Review": {"EN": "practicing math again", "RW": "gusubira ku mibare y'ibanze", "FR": "s'entraîner sur les calculs"},
    "ReadSimple": {"EN": "reading simple words", "RW": "gusoma amagambo yoroshye", "FR": "lire des mots simples"},
    "ReadSimple_Review": {"EN": "practicing reading again", "RW": "gusubira ku gusoma", "FR": "s'entraîner sur la lecture"}
}

NEXT_MOMENT_DESCRIPTIONS = {
    "Next learning activity": {
        "EN": "continue with the next learning activity",
        "RW": "dukomeze isomo rikurikira",
        "FR": "continuer avec la prochaine activite",
    },
    "Learning game": {
        "EN": "play a short learning game",
        "RW": "dukine umukino mugufi wo kwiga",
        "FR": "jouer a un petit jeu d'apprentissage",
    },
    "Story time": {
        "EN": "enjoy a short story time",
        "RW": "twumve agakuru gato",
        "FR": "ecouter une petite histoire",
    },
    "Rest and story time": {
        "EN": "take a tiny rest, then enjoy a short story",
        "RW": "turuhuke gato, hanyuma twumve agakuru",
        "FR": "prendre une petite pause, puis ecouter une histoire",
    },
}

INTRO_CARTOON = {
    "RW": ["Yego kabisa!", "Wawu!", "Urakoze cyane!", "Bip-bop, reba!", "braaavooo!", "Yego!", "Wabikoze!"],
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

class BuddyEngine:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="phi3", state_file="data/student_state.json"):
        self.gemini_api_keys = self._load_gemini_api_keys()
        self.gemini_api_key = self.gemini_api_keys[0] if self.gemini_api_keys else ""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.state_file = state_file
        self.ollama_enabled = True

    def _load_gemini_api_keys(self):
        keys = []

        combined_keys = os.environ.get("GEMINI_API_KEYS", "")
        for key in combined_keys.replace(";", ",").split(","):
            key = key.strip()
            if key and key not in keys:
                keys.append(key)

        for env_name in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GOOGLE_API_KEY"):
            key = os.environ.get(env_name, "").strip()
            if key and key not in keys:
                keys.append(key)

        return keys

    def _mask_key(self, key):
        if not key:
            return "<missing>"
        if len(key) <= 8:
            return "****"
        return f"{key[:4]}...{key[-4:]}"

    def _parse_http_error(self, error):
        try:
            body = error.read().decode("utf-8", errors="replace")
            data = json.loads(body)
            message = data.get("error", {}).get("message", body)
        except Exception:
            message = getattr(error, "reason", "") or str(error)
        return f"HTTP {error.code}: {message}"

    def _expected_tags(self, language_preference):
        if language_preference == "RW-EN":
            return ("[RW]", "[EN]")
        if language_preference == "RW-FR":
            return ("[RW]", "[FR]")
        if language_preference == "RW":
            return ("[RW]",)
        if language_preference == "FR":
            return ("[FR]",)
        return ("[EN]",)

    def _is_usable_ai_response(self, text, language_preference):
        text = (text or "").strip()
        if not text:
            return False, "empty response"

        missing_tags = [tag for tag in self._expected_tags(language_preference) if tag not in text]
        if missing_tags:
            return False, f"missing language tag(s): {', '.join(missing_tags)}"

        words_without_tags = text
        for tag in ("[RW]", "[EN]", "[FR]"):
            words_without_tags = words_without_tags.replace(tag, " ")
        word_count = len(words_without_tags.split())
        minimum_words = 8 if language_preference in ("RW", "EN", "FR") else 12
        if word_count < minimum_words:
            return False, f"too short ({word_count} words)"

        return True, ""

    def _extract_gemini_text(self, response_data):
        parts = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return " ".join(part.get("text", "") for part in parts).strip()

    def _json_from_text(self, text):
        text = (text or "").strip()
        if not text:
            return None

        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]

        try:
            return json.loads(text)
        except Exception:
            return None

    def _format_ai_response(self, response_data, language_preference):
        raw_text = self._extract_gemini_text(response_data)
        parsed = self._json_from_text(raw_text)

        if parsed:
            rw = str(parsed.get("rw", "")).strip()
            en = str(parsed.get("en", "")).strip()
            fr = str(parsed.get("fr", "")).strip()

            if language_preference == "RW-EN" and rw and en:
                return f"[RW] {rw} [EN] {en}", raw_text
            if language_preference == "RW-FR" and rw and fr:
                return f"[RW] {rw} [FR] {fr}", raw_text
            if language_preference == "RW" and rw:
                return f"[RW] {rw}", raw_text
            if language_preference == "FR" and fr:
                return f"[FR] {fr}", raw_text
            if language_preference not in ("RW-EN", "RW-FR", "RW", "FR") and en:
                return f"[EN] {en}", raw_text

        return raw_text, raw_text

    def _is_online(self):
        try:
            socket.setdefaulttimeout(1)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            return True
        except Exception:
            return False

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
        activity = str(activity).strip()
        default_desc = {"EN": activity.lower().replace("_", " "), "RW": activity.lower().replace("_", " "), "FR": activity.lower().replace("_", " ")}
        desc = ACTIVITY_DESCRIPTIONS.get(activity, default_desc)
        return desc.get(lang, desc["EN"])

    def _get_next_moment_desc(self, next_moment, lang):
        desc = NEXT_MOMENT_DESCRIPTIONS.get(next_moment, NEXT_MOMENT_DESCRIPTIONS["Next learning activity"])
        return desc.get(lang, desc["EN"])

    def _call_gemini(self, system_prompt, user_prompt, language_preference):
        if not self.gemini_api_keys:
            print(" [Buddy] Online helper is not set up yet")
            return None

        print(" [Buddy] Checking online helper...")

        base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 512,
                "responseMimeType": "application/json",
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }

        for index, api_key in enumerate(self.gemini_api_keys, start=1):
            is_oauth_token = api_key.startswith("ya29.")
            url = base_url if is_oauth_token else f"{base_url}?key={api_key}"
            headers = {"Content-Type": "application/json"}
            if is_oauth_token:
                headers["Authorization"] = f"Bearer {api_key}"

            try:
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=7) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    text, raw_text = self._format_ai_response(res_data, language_preference)
                    is_usable, reason = self._is_usable_ai_response(text, language_preference)
                    if is_usable:
                        print(" [Buddy] Online helper is ready")
                        return text
                    preview = (raw_text or "").replace("\n", " ")[:80]
                    print(f" [Buddy] Online helper gave a short answer, trying again...")
            except urllib.error.HTTPError as e:
                details = self._parse_http_error(e)
                if e.code == 429 or "RESOURCE_EXHAUSTED" in details:
                    print(" [Buddy] Online helper is busy right now")
                else:
                    print(" [Buddy] Online helper could not answer")
            except Exception as e:
                print(" [Buddy] Online helper could not answer")
        return None

    def _build_prompts(
        self,
        student_name,
        precision,
        current_act,
        next_task,
        language_preference,
        jerk_index,
        session_minutes=0,
        next_moment="Next learning activity",
        next_moment_note="Continue softly with the next activity.",
    ):
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")
        moment_en = self._get_next_moment_desc(next_moment, "EN")
        moment_rw = self._get_next_moment_desc(next_moment, "RW")
        moment_fr = self._get_next_moment_desc(next_moment, "FR")

        base_rules = (
            "You are Buddy, a warm AI learning friend for toddlers aged 3 to 5 in an inclusive adaptive learning platform. "
            "The child may move between tracing, games, story time, reading, numbers, and gentle rest. "
            "Reply like a kind preschool teacher and cheerful learning friend: simple, playful, calm, and encouraging. "
            "Use short toddler-friendly words. Do not mention scores, APIs, models, or technical terms. "
            "Do not ask questions. Include praise, one gentle coaching idea, and the best next moment. "
            "If the child has studied for a long time, protect the child from getting tired. "
            "Write 2 short sentences per language, with enough warmth to feel like a real conversation. "
            "Keep each language under 28 words. "
            "Return only valid JSON with lowercase language keys. No markdown. No extra text."
        )

        if precision >= 0.7:
            coaching_goal = "Praise the child for trying well."
        else:
            coaching_goal = "Encourage the child to try again gently without making them feel bad."

        if jerk_index > 5.0:
            coaching_goal += " Remind them to move the hand slowly and stay calm."

        if session_minutes >= 30:
            coaching_goal += " The child has studied for a long time, so recommend a tiny rest before more learning."
        elif session_minutes >= 20:
            coaching_goal += " The child has studied for a while, so recommend story time before another task."
        elif session_minutes >= 12:
            coaching_goal += " The child has studied for a little while, so recommend a quick learning game."

        if language_preference == "RW-EN":
            system_prompt = (
                f"{base_rules} Required JSON shape: "
                "{\"rw\":\"Kinyarwanda sentences\",\"en\":\"English sentences\"}"
            )
            user_prompt = (
                f"Child name: {student_name}. Current activity: {curr_en} / {curr_rw}. "
                f"Learning path: {next_en} / {next_rw}. Best next moment: {moment_en} / {moment_rw}. "
                f"Session time: about {session_minutes} minutes. Teacher note: {next_moment_note}. Goal: {coaching_goal}"
            )
        elif language_preference == "RW-FR":
            system_prompt = (
                f"{base_rules} Required JSON shape: "
                "{\"rw\":\"Kinyarwanda sentences\",\"fr\":\"French sentences\"}"
            )
            user_prompt = (
                f"Child name: {student_name}. Current activity: {curr_fr} / {curr_rw}. "
                f"Learning path: {next_fr} / {next_rw}. Best next moment: {moment_fr} / {moment_rw}. "
                f"Session time: about {session_minutes} minutes. Teacher note: {next_moment_note}. Goal: {coaching_goal}"
            )
        elif language_preference == "RW":
            system_prompt = f"{base_rules} Required JSON shape: {{\"rw\":\"Kinyarwanda sentences\"}}"
            user_prompt = (
                f"Child name: {student_name}. Current activity: {curr_rw}. Learning path: {next_rw}. "
                f"Best next moment: {moment_rw}. Session time: about {session_minutes} minutes. "
                f"Teacher note: {next_moment_note}. Goal: {coaching_goal}"
            )
        elif language_preference == "FR":
            system_prompt = f"{base_rules} Required JSON shape: {{\"fr\":\"French sentences\"}}"
            user_prompt = (
                f"Child name: {student_name}. Current activity: {curr_fr}. Learning path: {next_fr}. "
                f"Best next moment: {moment_fr}. Session time: about {session_minutes} minutes. "
                f"Teacher note: {next_moment_note}. Goal: {coaching_goal}"
            )
        else:
            system_prompt = f"{base_rules} Required JSON shape: {{\"en\":\"English sentences\"}}"
            user_prompt = (
                f"Child name: {student_name}. Current activity: {curr_en}. Learning path: {next_en}. "
                f"Best next moment: {moment_en}. Session time: about {session_minutes} minutes. "
                f"Teacher note: {next_moment_note}. Goal: {coaching_goal}"
            )

        return system_prompt, user_prompt

    def _call_openai(self, system_prompt, user_prompt, chat_history_list):
        if not self.openai_api_key:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        messages = [{"role": "system", "content": system_prompt}]
        for role, content in chat_history_list:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_prompt})
        
        payload = {"model": "gpt-4o-mini", "messages": messages, "max_tokens": 80, "temperature": 0.7}
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                        headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.openai_api_key}"}, method="POST")
            with urllib.request.urlopen(req, timeout=4) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception:
            return None

    def _call_ollama(self, system_prompt, user_prompt):
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {"temperature": 0.7, "max_tokens": 60}
        }
        try:
            req = urllib.request.Request(self.ollama_url, data=json.dumps(payload).encode("utf-8"),
                                        headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=2) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data.get("response", "").strip()
        except Exception:
            self.ollama_enabled = False
            return None

    def _generate_fallback(
        self,
        student_name,
        precision,
        current_act,
        next_task,
        language_preference,
        jerk_index=0.0,
        session_minutes=0,
        next_moment="Next learning activity",
    ):
        curr_en = self._get_act_desc(current_act, "EN")
        next_en = self._get_act_desc(next_task, "EN")
        curr_rw = self._get_act_desc(current_act, "RW")
        next_rw = self._get_act_desc(next_task, "RW")
        curr_fr = self._get_act_desc(current_act, "FR")
        next_fr = self._get_act_desc(next_task, "FR")
        moment_en = self._get_next_moment_desc(next_moment, "EN")
        moment_rw = self._get_next_moment_desc(next_moment, "RW")
        moment_fr = self._get_next_moment_desc(next_moment, "FR")
        rest_rw = "Turuhuke gato kugira ngo ukomeze wishimye."
        rest_en = "Let's take a tiny rest so learning stays fun."
        rest_fr = "Prenons une petite pause pour garder le plaisir."
        close_rw = rest_rw if session_minutes >= 30 else f"Noneho {moment_rw}."
        close_en = rest_en if session_minutes >= 30 else f"Now let's {moment_en}."
        close_fr = rest_fr if session_minutes >= 30 else f"Maintenant, on va {moment_fr}."

        intro_rw = random.choice(INTRO_CARTOON["RW"])
        intro_en = random.choice(INTRO_CARTOON["EN"])
        intro_fr = random.choice(INTRO_CARTOON["FR"])

        if jerk_index > 5.0:
            tremor_rw = random.choice(TREMOR_PHRASES["RW"])
            tremor_en = random.choice(TREMOR_PHRASES["EN"])
            tremor_fr = random.choice(TREMOR_PHRASES["FR"])
            if language_preference == "RW-EN":
                return f"[RW] {intro_rw} {tremor_rw} {close_rw} [EN] {intro_en} {tremor_en} {close_en}"
            elif language_preference == "RW-FR":
                return f"[RW] {intro_rw} {tremor_rw} {close_rw} [FR] {intro_fr} {tremor_fr} {close_fr}"
            elif language_preference == "RW":
                return f"[RW] {intro_rw} {tremor_rw} {close_rw}"
            elif language_preference == "FR":
                return f"[FR] {intro_fr} {tremor_fr} {close_fr}"
            else:
                return f"[EN] {intro_en} {tremor_en} {close_en}"

        if precision >= 0.7:
            praise_rw = random.choice(PRAISE_PHRASES["RW"])
            praise_en = random.choice(PRAISE_PHRASES["EN"])
            praise_fr = random.choice(PRAISE_PHRASES["FR"])
            if language_preference == "RW-EN":
                return f"[RW] {intro_rw} {praise_rw} kuri {curr_rw}! {close_rw} [EN] {intro_en} {praise_en} {close_en}"
            elif language_preference == "RW-FR":
                return f"[RW] {intro_rw} {praise_rw} kuri {curr_rw}! {close_rw} [FR] {intro_fr} {praise_fr} {close_fr}"
            elif language_preference == "RW":
                return f"[RW] {intro_rw} {praise_rw} kuri {curr_rw}! {close_rw}"
            elif language_preference == "FR":
                return f"[FR] {intro_fr} {praise_fr} {close_fr}"
            else:
                return f"[EN] {intro_en} {praise_en} {close_en}"
        else:
            enc_rw = random.choice(ENCOURAGE_PHRASES["RW"])
            enc_en = random.choice(ENCOURAGE_PHRASES["EN"])
            enc_fr = random.choice(ENCOURAGE_PHRASES["FR"])
            if language_preference == "RW-EN":
                return f"[RW] {intro_rw} {enc_rw} kuri {curr_rw}! {close_rw} [EN] {intro_en} {enc_en} {close_en}"
            elif language_preference == "RW-FR":
                return f"[RW] {intro_rw} {enc_rw} kuri {curr_rw}! {close_rw} [FR] {intro_fr} {enc_fr} {close_fr}"
            elif language_preference == "RW":
                return f"[RW] {intro_rw} {enc_rw} kuri {curr_rw}! {close_rw}"
            elif language_preference == "FR":
                return f"[FR] {intro_fr} {enc_fr} {close_fr}"
            else:
                return f"[EN] {intro_en} {enc_en} {close_en}"

    def run_pipeline(
        self,
        student_name,
        precision,
        current_act,
        next_task,
        language_preference="RW-EN",
        jerk_index=0.0,
        session_minutes=0,
        next_moment="Next learning activity",
        next_moment_note="Continue softly with the next activity.",
    ):
        state = self._load_state()
        student_record = state.setdefault(student_name, {})
        if not isinstance(student_record, dict):
            student_record = {"chat_history": []}
            state[student_name] = student_record

        chat_history = student_record.setdefault("chat_history", [])
        if not isinstance(chat_history, list):
            chat_history = []
            student_record["chat_history"] = chat_history

        chat_history_list = chat_history[-4:]

        system_prompt, user_prompt = self._build_prompts(
            student_name,
            precision,
            current_act,
            next_task,
            language_preference,
            jerk_index,
            session_minutes=session_minutes,
            next_moment=next_moment,
            next_moment_note=next_moment_note,
        )

        response_text = None
        online = self._is_online()

        if online and self.gemini_api_key:
            response_text = self._call_gemini(system_prompt, user_prompt, language_preference)

        if not response_text and self.openai_api_key:
            response_text = self._call_openai(system_prompt, user_prompt, chat_history_list)

        if not response_text:
            if not online:
                response_text = self._call_ollama(system_prompt, user_prompt)
            if not response_text:
                print(" [Buddy] Using offline helper")
                response_text = self._generate_fallback(
                    student_name,
                    precision,
                    current_act,
                    next_task,
                    language_preference,
                    jerk_index,
                    session_minutes=session_minutes,
                    next_moment=next_moment,
                )

        # Update state
        student_summary = f"Drew {self._get_act_desc(current_act, 'EN')} with {int(precision * 100)}% accuracy. Jerk: {jerk_index:.1f}."
        chat_history_list.append(("user", student_summary))
        chat_history_list.append(("assistant", response_text or ""))
        if len(chat_history_list) > 10:
            chat_history_list = chat_history_list[-10:]
        student_record["chat_history"] = chat_history_list
        self._save_state(state)

        return response_text
