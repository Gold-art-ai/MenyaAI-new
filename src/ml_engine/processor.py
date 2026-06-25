import numpy as np

class ActivityProcessor:
    """
    Translates raw touch-screen coordinates into ML features.
    Advanced version: Adds Dynamic Time Warping (DTW) and kinematics (velocity, acceleration, jerk).
    """
    def __init__(self, target_coords):
        """
        target_coords: List of (x, y) tuples representing the 'perfect' shape.
        """
        self.target_path = np.array(target_coords)

    def _interpolate_path(self, path, num_samples=50):
        """Interpolates path to a uniform number of points to stabilize time-series differentials."""
        if len(path) < 2:
            if len(path) == 1:
                return np.repeat(path, num_samples, axis=0)
            return np.zeros((num_samples, 2))
        
        t_orig = np.linspace(0, 1, len(path))
        t_new = np.linspace(0, 1, num_samples)
        x_interp = np.interp(t_new, t_orig, path[:, 0])
        y_interp = np.interp(t_new, t_orig, path[:, 1])
        return np.column_stack((x_interp, y_interp))

    def _compute_dtw(self, path1, path2):
        """Computes basic Dynamic Time Warping (DTW) cumulative distance between two 2D paths."""
        n, m = len(path1), len(path2)
        dtw_matrix = np.full((n + 1, m + 1), np.inf)
        dtw_matrix[0, 0] = 0
        
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = np.linalg.norm(path1[i - 1] - path2[j - 1])
                dtw_matrix[i, j] = cost + min(dtw_matrix[i - 1, j],
                                              dtw_matrix[i, j - 1],
                                              dtw_matrix[i - 1, j - 1])
        return dtw_matrix[n, m]

    def calculate_metrics(self, user_coords, time_taken, lifts):
        """
        user_coords: List of (x, y) tuples from the tablet touch sensor.
        """
        if not user_coords:
            return {
                "precision": 0.0,
                "smoothness": 1.0,
                "time": time_taken,
                "lifts": lifts,
                "dtw_distance": 0.0,
                "jerk_index": 0.0,
                "velocity_variance": 0.0
            }

        user_path = np.array(user_coords)
        
        # 1. ACCURACY (Average Euclidean Distance) - Backwards compatible
        total_deviation = 0
        for point in user_path:
            distances = np.linalg.norm(self.target_path - point, axis=1)
            total_deviation += np.min(distances)
        
        avg_deviation = total_deviation / len(user_path)
        precision_score = max(0.0, 1 - (avg_deviation / 100))

        # 2. SMOOTHNESS (Path Length Ratio) - Backwards compatible
        user_len = np.sum(np.sqrt(np.sum(np.diff(user_path, axis=0)**2, axis=1)))
        target_len = np.sum(np.sqrt(np.sum(np.diff(self.target_path, axis=0)**2, axis=1)))
        smoothness = user_len / target_len if target_len > 0 else 1.0

        # 3. ADVANCED MOTOR METRICS
        # Interpolate paths to a standard length of 50 samples for consistent differentials and fast DTW
        target_interp = self._interpolate_path(self.target_path, 50)
        user_interp = self._interpolate_path(user_path, 50)
        
        # A. Dynamic Time Warping (DTW) distance (sequence-sensitive)
        dtw_distance = self._compute_dtw(target_interp, user_interp)

        # B. Kinematics: Velocity, Acceleration, Jerk (Tremor detection)
        # Assume sample time delta dt = time_taken / 50. Limit min time_taken to avoid division by zero.
        dt = max(0.05, time_taken) / 50.0
        
        diffs = np.diff(user_interp, axis=0)
        step_distances = np.sqrt(np.sum(diffs**2, axis=1))
        velocities = step_distances / dt
        
        accelerations = np.diff(velocities) / dt
        jerks = np.diff(accelerations) / dt
        
        # Root Mean Square of jerk represents the tremble intensity
        jerk_rms = np.sqrt(np.mean(jerks**2)) if len(jerks) > 0 else 0.0
        velocity_var = np.var(velocities) if len(velocities) > 0 else 0.0

        return {
            "precision": round(precision_score, 2),
            "smoothness": round(smoothness, 2),
            "time": time_taken,
            "lifts": lifts,
            # Advanced fields
            "dtw_distance": round(dtw_distance, 2),
            "jerk_index": round(jerk_rms, 2),
            "velocity_variance": round(velocity_var, 2)
        }