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
        
        # Correlate smoothness with lifts and random noise:
        # 1.0 is perfectly smooth, > 1.5 is shaky/scribbling
        smoothness = 1.0 + (lifts * 0.1) + np.random.uniform(-0.1, 0.25)
        smoothness = max(1.0, round(smoothness, 2))
        
        # LOGIC FOR THE AI TO LEARN:
        # 1. Advance: If good precision, few lifts, and steady hand
        if precision >= 0.75 and lifts <= 2 and smoothness < 1.4:
            target = activities[current_lvl + 1]
        # 2. Review: If precision is low, or lifts are too high, or very shaky (smoothness > 1.6)
        elif precision < 0.55 or lifts > 4 or smoothness > 1.6:
            target = activities[current_lvl] + "_Review"
        # 3. Stay: Okay precision but still unsteady, needs more practice
        else:
            target = activities[current_lvl]
            
        data.append([activities[current_lvl], precision, smoothness, lifts, time_spent, target])

    # Reinforce clear advancement and review patterns for every activity
    for i, act in enumerate(activities[:-1]):
        next_act = activities[i + 1]
        # Strong advancement examples (high precision, smooth, low lifts)
        for p in [0.80, 0.85, 0.90, 0.95]:
            for s in [1.0, 1.1, 1.2]:
                data.append([act, p, s, 0, 15.0, next_act])
                data.append([act, p, s, 1, 20.0, next_act])
        # Clear review examples
        data.append([act, 0.40, 1.80, 5, 45.0, act + "_Review"])
        data.append([act, 0.30, 1.90, 7, 50.0, act + "_Review"])
    # ReadSimple stays at ReadSimple (final level)
    data.append(["ReadSimple", 0.90, 1.10, 0, 15.0, "ReadSimple"])
    data.append(["ReadSimple", 0.40, 1.80, 5, 45.0, "ReadSimple_Review"])

    df = pd.DataFrame(data, columns=['current_activity', 'precision', 'smoothness', 'lifts', 'time_spent', 'recommended_activity'])
    df.to_csv(output_path, index=False)
    print(f"Dataset generated at {output_path} ({len(df)} rows)")

if __name__ == "__main__":
    generate_toddler_dataset()