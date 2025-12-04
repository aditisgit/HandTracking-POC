import numpy as np
from config.config import THRESHOLD_SAFE, THRESHOLD_WARNING, CIRCLE_RADIUS, WARNING_BAND, DEBOUNCE_FRAMES

class DistanceLogic:
    def __init__(self):
        """
        Initialize the DistanceLogic with predefined thresholds.
        """
        self.threshold_safe = THRESHOLD_SAFE
        self.threshold_warning = THRESHOLD_WARNING
        self.debounce_frames = DEBOUNCE_FRAMES
        self.state_history = []

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
        Determine the state (SAFE, WARNING, DANGER) based on the distance with hysteresis.
        Args:
            distance (float): The calculated distance.
        Returns:
            str: The state ('SAFE', 'WARNING', 'DANGER').
        """
        if distance is None:
            return "SAFE"

        # Hysteresis buffer to prevent flickering
        hysteresis = 5

        # Get the last state (or default to SAFE)
        current_state = self.state_history[-1] if self.state_history else "SAFE"

        new_state = current_state

        if current_state == "SAFE":
            if distance <= CIRCLE_RADIUS:
                new_state = "DANGER"
            elif distance <= CIRCLE_RADIUS + WARNING_BAND:
                new_state = "WARNING"
        
        elif current_state == "WARNING":
            if distance <= CIRCLE_RADIUS:
                new_state = "DANGER"
            elif distance > CIRCLE_RADIUS + WARNING_BAND + hysteresis:
                new_state = "SAFE"
        
        elif current_state == "DANGER":
            if distance > CIRCLE_RADIUS + hysteresis:
                if distance <= CIRCLE_RADIUS + WARNING_BAND + hysteresis:
                    new_state = "WARNING"
                else:
                    new_state = "SAFE"

        self.state_history.append(new_state)
        if len(self.state_history) > self.debounce_frames:
            self.state_history.pop(0)

        # Debounce logic: return the most frequent state in the last N frames
        return max(set(self.state_history), key=self.state_history.count)

if __name__ == "__main__":
    # Test the DistanceLogic module
    logic = DistanceLogic()

    point_a = (100, 100)
    point_b = (150, 150)

    distance = logic.calculate_distance(point_a, point_b)
    state = logic.determine_state(distance)

    print(f"Distance: {distance:.2f}")
    print(f"State: {state}")