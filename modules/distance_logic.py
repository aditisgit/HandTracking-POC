import numpy as np
from config.config import THRESHOLD_SAFE, THRESHOLD_WARNING

class DistanceLogic:
    def __init__(self):
        """
        Initialize the DistanceLogic with predefined thresholds.
        """
        self.threshold_safe = THRESHOLD_SAFE
        self.threshold_warning = THRESHOLD_WARNING

    def calculate_distance(self, point1, point2):
        """
        Calculate the Euclidean distance between two points.
        Args:
            point1 (tuple): Coordinates of the first point (x1, y1).
            point2 (tuple): Coordinates of the second point (x2, y2).
        Returns:
            float: Euclidean distance between the two points.
        """
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def determine_state(self, distance):
        """
        Determine the state (SAFE, WARNING, DANGER) based on the distance.
        Args:
            distance (float): The calculated distance.
        Returns:
            str: The state ('SAFE', 'WARNING', 'DANGER').
        """
        if distance > self.threshold_safe:
            return "SAFE"
        elif self.threshold_warning < distance <= self.threshold_safe:
            return "WARNING"
        else:
            return "DANGER"

if __name__ == "__main__":
    # Test the DistanceLogic module
    logic = DistanceLogic()

    point_a = (100, 100)
    point_b = (150, 150)

    distance = logic.calculate_distance(point_a, point_b)
    state = logic.determine_state(distance)

    print(f"Distance: {distance:.2f}")
    print(f"State: {state}")