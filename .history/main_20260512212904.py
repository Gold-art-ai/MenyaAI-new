from data.raw_process import generate_toddler_dataset
from src.ml_engine.trainer import train_recommender
from src.ml_engine.recommender import RecommendationEngine

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

    print ()
if __name__ == "__main__":
    test_system()