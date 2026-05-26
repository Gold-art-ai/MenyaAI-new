from src.ml_engine.recommender import RecommendationEngine
from src.buddy_service.buddy_ai import BuddyAI  # Use the AI version we just made
from src.ml_engine.processor import ActivityProcessor


def run_ml_pipeline(current_act, user_touches, time, lifts):
    """Handles the math and the recommendation quietly."""
    # 1. Process Raw Data
    target_path = [(100, 100), (150, 150), (200, 100)]  # Example target
    processor = ActivityProcessor(target_path)
    metrics = processor.calculate_metrics(user_touches, time, lifts)

    # 2. Get AI Recommendation
    engine = RecommendationEngine()
    next_task = engine.get_recommendation(
        current_act, metrics["precision"], lifts, time
    )

    return metrics, next_task


def main():
    print("[START] Umwana AI Engine Started")
    
    print("\nSelect Preferred Language:")
    print("1. Kinyarwanda to English (Code-Switching)")
    print("2. Kinyarwanda to French (Code-Switching)")
    print("3. Pure Kinyarwanda")
    print("4. Pure English")
    print("5. Pure French")
    choice = input("Enter choice (1-5, default is 1): ").strip()
    
    lang_map = {
        "1": "RW-EN",
        "2": "RW-FR",
        "3": "RW",
        "4": "EN",
        "5": "FR"
    }
    language_preference = lang_map.get(choice, "RW-EN")

    # Input Simulation (This replaces the messy dataset generation logs)
    student = "Gloria"
    current_activity = "Shapes"
    mock_touches = [(105, 102), (148, 155), (205, 95)]

    # 1. Run the AI Logic
    metrics, next_task = run_ml_pipeline(current_activity, mock_touches, 15, 1)

    # 2. Display ONLY the critical results
    print(f"\n [REPORT] Student: {student}")
    print(f"   - Precision: {metrics['precision'] * 100}%")
    print(f"   - Next Activity: {next_task}")

    # 3. Trigger the Real Buddy AI (The Voice part)
    print("\n [BUDDY] Speaking to child...")
    buddy = BuddyAI()
    buddy.give_praise(student, metrics["precision"], current_activity, next_task, language_preference)


if __name__ == "__main__":
    # Note: We removed generate_toddler_dataset() and train_recommender()
    # because you only need to run those ONCE, not every time you test!
    main()
