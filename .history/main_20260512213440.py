from data.raw_process import generate_toddler_dataset
from src.ml_engine.trainer import train_recommender
from src.ml_engine.recommender import RecommendationEngine
from src.analytics.report_gen import TeacherAnalyst
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
    
    advice = analyst.get_individual_advice("Joshua", 1.0, 6)
     
if __name__ == "__main__":
    test_system()