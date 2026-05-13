from data.raw_process import generate_toddler_dataset
from src.ml_engine.trainer import train_recommender
from src.ml_engine.recommender import RecommendationEngine
from src.analytics.report_gen import TeacherAnalyst
from src.buddy_service.buddy_logic import BuddyService
from src.ml_engine.processor import ActivityProcessor
def test_system():
    generate_toddler_dataset()

    train_recommender()

    engine = RecommendationEngine()

    result = engine.get_recommendation("Shapes", 0.55,0,15)

    print("\n--- Test Result ----")
    print(f"Kid performed: Shapes")
    print(f"AI Recommended: {result}")

    if "Shapes" in result:
        print("Success: AI correctly leveled up student up!")
    else:
        print("Failed: AI did not do the recognition well!")

    print("\n=== Generating Teacher report === ")
    analyst = TeacherAnalyst()
    class_reports = analyst.generate_class_report()
    
    print(f"Kinyarwanda: {class_reports['RW']}")
    print(f"English: {class_reports['EN']}")
    print(f"French: {class_reports['FR']}")
    
    advice = analyst.get_individual_advice("Joshua", 0.70, 9)
    print(f"\n Advice for Joshua: {advice['EN']}")
    
    print("\n--- BUDDY VOICE FEEDBACK ---")
    buddy = BuddyService()
    
    # Simulate a child finishing with low precision in Kinyarwanda
    low_score_feedback = buddy.get_buddy_response(0.4, language="RW")
    print(f"Buddy says (Low Score - RW): {low_score_feedback}")
    
    # Simulate a child finishing with high precision in French
    high_score_feedback = buddy.get_buddy_response(0.95, language="FR")
    print(f"Buddy says (High Score - FR): {high_score_feedback}")
    
    target_circle = [(100, 100), (150, 150), (200, 100), (150, 50)]
    user_touch = 
if __name__ == "__main__":
    test_system()