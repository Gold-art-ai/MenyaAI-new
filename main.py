from pathlib import Path
import sys

from src.ml_engine.processor import ActivityProcessor
from src.ml_engine.recommender import RecommendationEngine


PROJECT_ROOT = Path(__file__).resolve().parent
BUDDY_SERVICE_DIR = PROJECT_ROOT / "src" / "buddy_service"
if str(BUDDY_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(BUDDY_SERVICE_DIR))

from buddy_ai import BuddyAI


ACTIVITIES = {
    "1": ("Lines", "Tracing lines"),
    "2": ("Shapes", "Drawing simple shapes"),
    "3": ("Letters", "Writing letters"),
    "4": ("Numbers", "Tracing numbers"),
    "5": ("Words", "Writing simple words"),
    "6": ("MathBasics", "Simple counting and math"),
    "7": ("ReadSimple", "Reading simple words"),
}

LANGUAGES = {
    "1": ("RW-EN", "Kinyarwanda + English"),
    "2": ("RW-FR", "Kinyarwanda + French"),
    "3": ("RW", "Kinyarwanda only"),
    "4": ("EN", "English only"),
    "5": ("FR", "French only"),
}

DRAWING_LEVELS = {
    "1": {
        "label": "Great try",
        "touches": [(102, 101), (150, 148), (198, 102)],
        "time": 12,
        "lifts": 0,
    },
    "2": {
        "label": "Good try",
        "touches": [(108, 104), (146, 158), (207, 96)],
        "time": 16,
        "lifts": 1,
    },
    "3": {
        "label": "Needs more practice",
        "touches": [(125, 118), (133, 178), (225, 82)],
        "time": 24,
        "lifts": 3,
    },
}

HAND_LEVELS = {
    "1": ("Calm and steady", 2.0),
    "2": ("A little shaky", 5.5),
    "3": ("Needs slow gentle guidance", 8.0),
}

SESSION_LENGTHS = {
    "1": ("Just started", 5),
    "2": ("Learning for a little while", 15),
    "3": ("Learning for a long time", 25),
    "4": ("Looks tired today", 35),
}

TARGET_PATH = [(100, 100), (150, 150), (200, 100)]


def ask_choice(title, choices, default):
    print(f"\n{title}")
    for key, value in choices.items():
        label = value[1] if isinstance(value, tuple) else value["label"]
        print(f"{key}. {label}")

    answer = input(f"Choose one [{default}]: ").strip()
    return answer if answer in choices else default


def run_learning_pipeline(student_name, current_activity, drawing_info):
    processor = ActivityProcessor(TARGET_PATH)
    metrics = processor.calculate_metrics(
        drawing_info["touches"],
        drawing_info["time"],
        drawing_info["lifts"],
    )

    recommender = RecommendationEngine()
    next_task = recommender.get_recommendation(
        current_activity=current_activity,
        precision=metrics["precision"],
        smoothness=metrics["smoothness"],
        lifts=drawing_info["lifts"],
        time_spent=drawing_info["time"],
        student_name=student_name,
    )

    return metrics, next_task


def choose_next_moment(next_task, session_minutes):
    if session_minutes >= 30:
        return (
            "Rest and story time",
            "Take a tiny rest, then enjoy a short story connected to learning.",
        )
    if session_minutes >= 20:
        return (
            "Story time",
            f"Use a short story that gently prepares the child for {next_task}.",
        )
    if session_minutes >= 12:
        return (
            "Learning game",
            f"Play a quick game before moving into {next_task}.",
        )
    return (
        "Next learning activity",
        f"Continue softly with {next_task}.",
    )


def explain_progress(metrics, next_task, drawing_label, hand_label, next_moment_label, next_moment_note):
    score_percent = int(metrics["precision"] * 100)

    if score_percent >= 80:
        child_summary = "The child is doing very well."
    elif score_percent >= 60:
        child_summary = "The child is improving and should keep practicing."
    else:
        child_summary = "The child needs a slower, easier practice moment."

    print("\n" + "=" * 48)
    print("              LEARNING SESSION SUMMARY")
    print("=" * 48)
    print(f"Drawing result: {drawing_label}")
    print(f"Hand movement: {hand_label}")
    print(f"Friendly progress: {score_percent}% ready")
    print(f"Teacher note: {child_summary}")
    print(f"Learning path: {next_task}")
    print(f"Best next moment: {next_moment_label}")
    print(f"Why: {next_moment_note}")


def main():
    print("\n" + "=" * 48)
    print("              MENYAAI LEARNING DEMO")
    print("=" * 48)
    print("This demo shows how MenyaAI watches a child's practice,")
    print("chooses the next activity, and lets Buddy give friendly help.")

    student_name = input("\nChild name [Amaury]: ").strip() or "Amaury"

    language_choice = ask_choice("Buddy language", LANGUAGES, "1")
    language_preference, language_label = LANGUAGES[language_choice]

    activity_choice = ask_choice("What is the child practicing now?", ACTIVITIES, "1")
    current_activity, activity_label = ACTIVITIES[activity_choice]

    buddy = BuddyAI()

    while True:
        print(f"\n--- Practice Session: {current_activity} ---")

        drawing_choice = ask_choice("How close was the child's drawing?", DRAWING_LEVELS, "2")
        drawing_info = DRAWING_LEVELS[drawing_choice]

        hand_choice = ask_choice("How steady was the child's hand?", HAND_LEVELS, "1")
        hand_label, hand_guidance_score = HAND_LEVELS[hand_choice]

        session_choice = ask_choice("How long has the child been learning today?", SESSION_LENGTHS, "2")
        session_label, session_minutes = SESSION_LENGTHS[session_choice]

        print("\nMenyaAI is checking the learning moment...")
        metrics, next_task = run_learning_pipeline(student_name, current_activity, drawing_info)
        next_moment_label, next_moment_note = choose_next_moment(next_task, session_minutes)

        explain_progress(
            metrics,
            next_task,
            drawing_info["label"],
            hand_label,
            next_moment_label,
            next_moment_note,
        )

        print("\nBuddy is preparing a friendly message...")
        buddy.give_praise(
            student_name=student_name,
            precision=metrics["precision"],
            current_act=current_activity,
            next_task=next_task,
            language_preference=language_preference,
            jerk_index=hand_guidance_score,
            velocity_variance=metrics.get("velocity_variance", 0.0),
            session_minutes=session_minutes,
            next_moment=next_moment_label,
            next_moment_note=next_moment_note,
        )

        # Set the next session's starting activity to the recommended task
        current_activity = next_task

        choice = input("\nContinue to the next session? (y/n) [y]: ").strip().lower() or "y"
        if choice == 'n':
            print("Goodbye! Thank you for using MenyaAI! 👋")
            break


if __name__ == "__main__":
    main()
