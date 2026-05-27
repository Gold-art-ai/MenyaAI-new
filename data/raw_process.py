import pandas as pd
import numpy as np

def generate_toddler_dataset(output_path='data/toddler_progress.csv'):
    np.random.seed(42)
    rows = 1500
    
    # Levels: 0=Lines, 1=Shapes, 2=Letters, 3=Numbers, 4=Words, 5=MathBasics, 6=ReadSimple
    activities = ['Lines', 'Shapes', 'Letters', 'Numbers', 'Words', 'MathBasics', 'ReadSimple']
    
    data = []
    for _ in range(rows):
        current_lvl = np.random.randint(0, len(activities) - 1) # Don't start at 'ReadSimple'
        precision = np.random.uniform(0.3, 0.98)
        lifts = np.random.randint(0, 8)
        time_spent = np.random.uniform(10, 60)
        
        # LOGIC FOR THE AI TO LEARN:
        # If precision is high and lifts are low, Move UP.
        if precision > 0.80 and lifts <= 1:
            target = activities[current_lvl + 1]
        # If precision is low, Repeat/Review.
        elif precision < 0.55:
            target = activities[current_lvl] + "_Review"
        else:
            target = activities[current_lvl] # Just stay put
            
        data.append([activities[current_lvl], precision, lifts, time_spent, target])

    # Also make sure the encoder knows about all review states by adding dummy samples at the end
    for act in activities:
        data.append([act, 0.90, 0, 15.0, act])
        data.append([act, 0.40, 5, 45.0, act + "_Review"])

    df = pd.DataFrame(data, columns=['current_activity', 'precision', 'lifts', 'time_spent', 'recommended_activity'])
    df.to_csv(output_path, index=False)
    print(f"Dataset generated at {output_path}")

if __name__ == "__main__":
    generate_toddler_dataset()