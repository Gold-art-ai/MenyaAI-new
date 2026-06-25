import joblib
import numpy as np  
import json
import os

PROGRESSION = ["Lines", "Shapes", "Letters", "Numbers", "Words", "MathBasics", "ReadSimple"]

class RecommendationEngine:
    def __init__(self, state_file="data/student_state.json"):
        self.model = joblib.load("models/recommender_model.pkl")
        self.le_act = joblib.load("models/le_act.pkl")
        self.le_target = joblib.load("models/le_target.pkl")
        self.state_file = state_file

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

    def get_recommendation(self, current_activity, precision, smoothness, lifts, time_spent, student_name="DefaultStudent"):
        # Extract base activity category (e.g. "Shapes" from "Shapes_Review")
        base_cat = current_activity.replace("_Review", "")
        
        # 1. Base Prediction using the RandomForest model
        act_enc = self.le_act.transform([base_cat])[0]
        prediction = self.model.predict([[act_enc, precision, smoothness, lifts, time_spent]])
        recommended = self.le_target.inverse_transform(prediction)[0]
        
        # 2. Load and update student learning state
        state = self._load_state()
        if student_name not in state:
            state[student_name] = {
                "latent_abilities": {p: 0.5 for p in PROGRESSION},
                "history": [],
                "stagnation_counter": 0
            }
            
        student_data = state[student_name]
        
        # Update latent motor/cognitive ability estimate using EMA
        if base_cat in student_data["latent_abilities"]:
            current_ability = student_data["latent_abilities"][base_cat]
            alpha = 0.3 # Weight for new performance
            student_data["latent_abilities"][base_cat] = round(
                (1 - alpha) * current_ability + alpha * precision, 2
            )
            
        # Add to history log
        student_data["history"].append({
            "activity": current_activity,
            "precision": precision,
            "smoothness": smoothness,
            "lifts": lifts,
            "time_spent": time_spent,
            "recommended_by_model": recommended
        })
        
        # Cap history list size
        if len(student_data["history"]) > 20:
            student_data["history"].pop(0)
            
        # 3. Detect Stagnation Loops
        # Check if they are getting repeated reviews and not achieving success
        last_activities = [h["activity"] for h in student_data["history"][-2:]]
        if len(last_activities) >= 2 and all("_Review" in act for act in last_activities) and precision < 0.6:
            student_data["stagnation_counter"] += 1
        else:
            student_data["stagnation_counter"] = 0
            
        final_recommendation = recommended
        
        # If student has been stuck on review sessions more than twice, downgrade category to rebuild confidence
        if student_data["stagnation_counter"] >= 2:
            try:
                idx = PROGRESSION.index(base_cat)
                if idx > 0:
                    final_recommendation = PROGRESSION[idx - 1]  # Recommend previous category
                else:
                    final_recommendation = "Lines"  # Keep at easiest and flag for assistance
                student_data["stagnation_counter"] = 0  # Reset counter
            except ValueError:
                pass
                
        # Save state changes
        self._save_state(state)
        
        return final_recommendation

        