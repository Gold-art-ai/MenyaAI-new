import joblib
import numpy as np  
class RecommendationEngine:
    def __init__(self):
        self.model= joblib.load("model/recommender_model.pkl")
        self.le_act= joblib.load("model/le_act.pkl")
        self.le_target= joblib.load("model/le_target.pkl")
    def get_recommendation(self, current_activity, precision, lifts, time_spent):
        act_enc = self.le_act.transform([current_activity])[0]
        prediction = self.model.predict([[act_enc, precision,lifts,time_spent]])
        return self.le_target.inverse_transform(prediction)[0]
        