from buddy_engine import BuddyEngine
from voice_engine import VoiceEngine

class BuddyAI:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="phi3", rw_voice="sw-KE-ZuriNeural", state_file="data/student_state.json"):
        self.voice = VoiceEngine(rw_voice=rw_voice)
        self.engine = BuddyEngine(ollama_url=ollama_url, model_name=model_name, state_file=state_file)

    def generate_response(
        self,
        student_name,
        precision,
        current_act,
        next_task,
        language_preference="RW-EN",
        jerk_index=0.0,
        velocity_variance=0.0,
        session_minutes=0,
        next_moment="Next learning activity",
        next_moment_note="Continue softly with the next activity.",
    ):
        return self.engine.run_pipeline(
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

    def give_praise(
        self,
        student_name,
        precision,
        current_act,
        next_task,
        language_preference="RW-EN",
        jerk_index=0.0,
        velocity_variance=0.0,
        session_minutes=0,
        next_moment="Next learning activity",
        next_moment_note="Continue softly with the next activity.",
    ):
        response_text = self.generate_response(
            student_name,
            precision,
            current_act,
            next_task,
            language_preference,
            jerk_index,
            velocity_variance,
            session_minutes,
            next_moment,
            next_moment_note,
        )
        print(f"\n [BUDDY RESPONSE]: {response_text}")
        self.voice.speak(response_text)
