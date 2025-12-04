import numpy as np
from collections import deque

class PointSmoother:
    def __init__(self, ema_alpha=0.4, median_N=5, max_displacement=100):
        """
        Initialize the PointSmoother.

        Parameters:
        - ema_alpha: Smoothing factor for EMA (0 < ema_alpha <= 1).
        - median_N: Number of points for median filtering.
        - max_displacement: Maximum allowed displacement to accept a new point.
        """
        self.ema_alpha = ema_alpha
        self.median_N = median_N
        self.max_displacement = max_displacement
        self.points = deque(maxlen=median_N)
        self.ema_point = None

    def update(self, raw_point):
        """
        Update the smoother with a new raw point.

        Parameters:
        - raw_point: Tuple (x, y) representing the new raw point.

        Returns:
        - Smoothed point (x, y) or None if the update is rejected.
        """
        if raw_point is None:
            return None

        # Add the raw point to the median filter buffer
        self.points.append(raw_point)

        # Compute the median of the last N points
        median_point = np.median(self.points, axis=0)

        # Initialize EMA if not already done
        if self.ema_point is None:
            self.ema_point = median_point

        # Calculate displacement from the current EMA point
        displacement = np.linalg.norm(np.array(raw_point) - np.array(self.ema_point))
        if displacement > self.max_displacement:
            return None  # Reject the update if displacement is too large

        # Update EMA toward the median point
        self.ema_point = (
            self.ema_alpha * median_point + (1 - self.ema_alpha) * self.ema_point
        )

        return tuple(self.ema_point)

    def get(self):
        """
        Get the current smoothed point.

        Returns:
        - Current smoothed point (x, y) or None if uninitialized.
        """
        return self.ema_point

class KalmanPoint:
    def __init__(self):
        """
        Initialize a simple Kalman filter for 2D point tracking.
        """
        self.state = np.zeros(4)  # [x, y, vx, vy]
        self.covariance = np.eye(4)
        self.process_noise = np.eye(4) * 0.01
        self.measurement_noise = np.eye(2) * 1.0
        self.measurement_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])

    def update(self, measurement):
        """
        Update the Kalman filter with a new measurement.

        Parameters:
        - measurement: Tuple (x, y) representing the new measurement.

        Returns:
        - Estimated state (x, y).
        """
        # Predict step
        self.state[:2] += self.state[2:]
        self.covariance += self.process_noise

        # Update step
        innovation = np.array(measurement) - self.measurement_matrix @ self.state
        innovation_covariance = (
            self.measurement_matrix @ self.covariance @ self.measurement_matrix.T
            + self.measurement_noise
        )
        kalman_gain = (
            self.covariance
            @ self.measurement_matrix.T
            @ np.linalg.inv(innovation_covariance)
        )
        self.state += kalman_gain @ innovation
        self.covariance -= (
            kalman_gain @ self.measurement_matrix @ self.covariance
        )

        return tuple(self.state[:2])

    def get(self):
        """
        Get the current estimated state.

        Returns:
        - Current estimated state (x, y).
        """
        return tuple(self.state[:2])