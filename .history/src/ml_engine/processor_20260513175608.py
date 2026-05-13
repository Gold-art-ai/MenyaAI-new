import numpy as np

class ActivityProcessor:
    """
    Translates raw touch-screen coordinates into ML features.
    """
    def __init__(self, target_coords):
        """
        target_coords: List of (x, y) tuples representing the 'perfect' shape.
        """
        self.target_path = np.array(target_coords)

    def calculate_metrics(self, user_coords, time_taken, lifts):
        """
        user_coords: List of (x, y) tuples from the tablet touch sensor.
        """
        if not user_coords:
            return {"precision": 0, "smoothness": 0, "time": time_taken, "lifts": lifts}

        user_path = np.array(user_coords)
        
        # 1. ACCURACY (Average Euclidean Distance)
        # For every point the user touched, find the distance to the nearest target point.
        total_deviation = 0
        for point in user_path:
            # Distance formula: sqrt((x2-x1)^2 + (y2-y1)^2)
            distances = np.linalg.norm(self.target_path - point, axis=1)
            total_deviation += np.min(distances)
        
        avg_deviation = total_deviation / len(user_path)
        
        # Normalize: 1.0 is perfect, 0.0 is 'off the rails'
        # We assume 100 pixels away is a total miss
        precision_score = max(0, 1 - (avg_deviation / 100))

        # 2. SMOOTHNESS (Path Length Ratio)
        # We compare the length of the user's path vs the ideal path length.
        user_len = np.sum(np.sqrt(np.sum(np.diff(user_path, axis=0)**2, axis=1)))
        target_len = np.sum(np.sqrt(np.sum(np.diff(self.target_path, axis=0)**2, axis=1)))
        
        # 1.0 = Smooth, 2.0+ = Trembling/Scribbling
        smoothness = user_len / target_len if target_len > 0 else 1

        return {
            "precision": round(precision_score, 2),
            "smoothness": round(smoothness, 2),
            "time": time_taken,
            "lifts": lifts
        }