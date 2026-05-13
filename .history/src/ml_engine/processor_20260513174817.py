import numpy as np

class ActivityProcessor:
    """
    Turns raw tablet touch data into ML-ready features.
    """
    def __init__(self, target_path_coords):
        # target_path_coords would be the 'ideal' points of the shape/letter
        self.target_path = np.array(target_path_coords)

    def calculate_metrics(self, user_touch_coords, time_taken, lifts):
        """
        user_touch_coords: List of (x, y) from the tablet
        """
        user_path = np.array(user_touch_coords)
        
        # 1. Calculate Deviation (Accuracy)
        # We find the distance from each user point to the nearest target point
        distances = []
        for point in user_path:
            dist = np.min(np.linalg.norm(self.target_path - point, axis=1))
            distances.append(dist)
        
        avg_deviation = np.mean(distances)
        # Normalize score: 1.0 is perfect, 0.0 is very messy
        precision_score = max(0, 1 - (avg_deviation / 50)) # 50 is a 'fail' threshold
        
        # 2. Calculate Smoothness (Speed/Fluidity)
        # If the path is much longer than the ideal path, they were shaking/scribbling
        user_path_length = np.sum(np.sqrt(np.sum(np.diff(user_path, axis=0)**2, axis=1)))
        target_path_length = np.sum(np.sqrt(np.sum(np.diff(self.target_path, axis=0)**2, axis=1)))
        smoothness_ratio = user_path_length / target_path_length

        return {
            "precision": round(precision_score, 2),
            "smoothness": round(smoothness_ratio, 2),
            "time": time_taken,
            "lifts": lifts
        }