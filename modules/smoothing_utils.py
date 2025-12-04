import numpy as np
from collections import deque

class PointSmoother:
    def __init__(self, window_size=5, alpha=0.2, max_displacement=50):
        """
        Initialize the PointSmoother with smoothing parameters.
        Args:
            window_size (int): Number of points for median smoothing.
            alpha (float): Smoothing factor for EMA.
            max_displacement (float): Maximum allowed displacement between points.
        """
        self.window_size = window_size
        self.alpha = alpha
        self.max_displacement = max_displacement
        self.points = deque(maxlen=window_size)
        self.ema_point = None

    def smooth(self, point):
        """
        Smooth the given point using median and EMA smoothing.
        Args:
            point (tuple): The new point (x, y) to smooth.
        Returns:
            tuple: The smoothed point (x, y).
        """
        if point is None:
            self.points.clear()
            self.ema_point = None
            return None

        # Handle sudden jumps: if displacement is too large, reset to new point
        if self.ema_point is not None:
            displacement = np.linalg.norm(np.array(point) - np.array(self.ema_point))
            if displacement > self.max_displacement:
                self.points.clear()
                self.ema_point = np.array(point)
                self.points.append(point)
                return point

        # Median smoothing
        self.points.append(point)
        median_point = np.median(self.points, axis=0)

        # EMA smoothing
        if self.ema_point is None:
            self.ema_point = median_point
        else:
            self.ema_point = self.alpha * np.array(median_point) + (1 - self.alpha) * np.array(self.ema_point)

        return tuple(self.ema_point.astype(int))
