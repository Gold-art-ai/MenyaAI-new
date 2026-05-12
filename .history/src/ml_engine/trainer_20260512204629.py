import pandas as pd 
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

def train_recommender(csv_path='data/toddler_progress.csv'):
    df = pd.read_csv(csv_path)
    
    le_act= LabelEncoder()
    le_target = LabelEncoder()

    df['current_activity'] = le_act.fit_transform(df['current_activity'])
    X = df[['current_activity', 'precision', 'lifts', 'time_spent']]
    y = le_target.fit_transform(df['recommended_activity'])

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X,y)

    joblib.dump(model, 'models/recommender_model.pkl')
    joblib.dump(le_act, 'models/le_act.pkl')
    joblib.dump(le_target, 'models/le_target.pkl')
    print("AI trainer: Model trained and saved to /models/")

if __name__ == "__main__":
    train_recommender()