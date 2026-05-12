import pandas as pd 
import numpy as np  
def generate_toddler_dataset(output_path = 'data/toddler_progress.csv'):
    np.random.seed(42)
    rows = 1000
    activities = ['Lines', 'Shapes', 'Letters','Numbers', 'Counting', 'Matching', 'Sorting', 'Words']
    data=[]
    for _ in range(rows):
        current_lvl = np.random.randint(0, 8)
        precision = np.random.uniform(0.3, 0.98)
        lifts = np.random.randint(0,8)
        time_spent = np.random.randint(10,60)

        if precision > 0.80 and lifts <= 1:
            target = activities[current_lvl +1]
        elif precision < 0.55:
            target = activities[current_lvl] + "_Review"
        else:
            target = activities[current_lvl]
        data.append([activities[current_lvl], precision, lifts, time_spent, target])
    df = pd.DataFrame(data, columns = ['current_activity', 'precision', 'lifts', 'time_spent', 'recommended_activity'])
    df.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path}")
   
if __name__ == "__main__":
    generate_toddler_dataset()

        
