from src.ml_engine.recommender import RecommendationEngine
from src.analytics.report_gen import TeacherAnalyst
from src.buddy_service.buddy_ai import BuddyAI  # Use the AI version we just made
from src.ml_engine.processor import ActivityProcessor

def run_ml_pipeline(current_act, user_touches, time, lifts):
    """Handles the math and the recommendation quietly."""
    # 1. Process Raw Data
    target_path = [(100, 100), (150, 150), (200, 100)] # Example target
    processor = ActivityProcessor(target_path)
    metrics = processor.calculate_metrics(user_touches, time, lifts)
    
    # 2. Get AI Recommendation
    engine = RecommendationEngine()
    next_task = engine.get_recommendation(current_act, metrics['precision'], lifts, time)
    
    return metrics, next_task

def main():
    print("🚀 --- Umwana AI Engine Started ---")
    
    # Input Simulation (This replaces the messy dataset generation logs)
    student = "Joshua"
    current_activity = "Shapes"
    mock_touches = [(105, 102), (148, 155), (205, 95)]
    
    # 1. Run the AI Logic
    metrics, next_task = run_ml_pipeline(current_activity, mock_touches, 15, 1)
    
    # 2. Display ONLY the critical results
    print(f"\n📊 [REPORT] Student: {student}")
    print(f"   - Precision: {metrics['precision'] * 100}%")
    print(f"   - Next Activity: {next_task}")

    # 3. Trigger the Real Buddy AI (The Voice part)
    print(f"\n🔊 [BUDDY] Speaking to child...")
    buddy = BuddyAI()
    buddy.give_praise(student, metrics['precision'])

    # 4. Teacher Insight
    analyst = TeacherAnalyst()
    advice = analyst.get_individual_advice(student, metrics['precision'], metrics['lifts'])
    print(f"\n👩‍🏫 [TEACHER ADVICE]: {advice['EN']}")

if __name__ == "__main__":
    # Note: We removed generate_toddler_dataset() and train_recommender()
    # because you only need to run those ONCE, not every time you test!
    main()