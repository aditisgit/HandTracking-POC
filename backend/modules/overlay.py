import cv2
from config.config import FONT, FONT_SCALE, FONT_COLOR, LINE_THICKNESS, CIRCLE_CENTER, CIRCLE_RADIUS

class Overlay:
    def __init__(self):
        """
        Initialize the Overlay class for drawing on frames.
        """
        self.font = FONT
        self.font_scale = FONT_SCALE
        self.font_color = FONT_COLOR
        self.line_thickness = LINE_THICKNESS
        self.last_contour = None  # Store the last detected contour for debugging
        self.last_hull = None  # Store the last detected hull for debugging

    def draw_state(self, frame, state):
        """
        Draw the current state (SAFE, WARNING, DANGER) on the frame.
        Args:
            frame (numpy.ndarray): The frame to draw on.
            state (str): The current state ('SAFE', 'WARNING', 'DANGER').
        Returns:
            numpy.ndarray: The frame with the state overlay.
        """
        if state == "SAFE":
            color = (0, 255, 0)  # Green
        elif state == "WARNING":
            color = (0, 255, 255)  # Yellow
        else:  # DANGER
            color = (0, 0, 255)  # Red

        # Draw the state text
        cv2.putText(frame, state, (10, 50), self.font, self.font_scale, color, self.line_thickness, cv2.LINE_AA)

        # Add a flashing overlay for DANGER state
        if state == "DANGER":
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
            alpha = 0.3  # Transparency factor
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        return frame

    def draw_virtual_object(self, frame, center=CIRCLE_CENTER, radius=CIRCLE_RADIUS):
        """
        Draw a virtual object (circle) on the frame.
        Args:
            frame (numpy.ndarray): The frame to draw on.
            center (tuple): The center of the virtual object (x, y).
            radius (int): The radius of the virtual object.
        Returns:
            numpy.ndarray: The frame with the virtual object drawn.
        """
        cv2.circle(frame, center, radius, (255, 0, 0), -1)  # Draw the circle (filled/opaque)
        return frame

    def draw_boundary_point(self, frame, point, contour=None, hull=None, debug=False):
        """
        Draw the closest boundary point as a white dot and optionally draw contours/hull for debugging.
        """
        if point is not None:
            try:
                point = (int(point[0]), int(point[1]))  # Ensure point is a tuple of integers
                cv2.circle(frame, point, 5, (255, 255, 255), -1)  # White dot
            except (TypeError, ValueError):
                pass  # Skip drawing if point is invalid

        if debug and contour is not None and hull is not None:
            # Draw contours and hull for debugging
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)  # Green contour
            cv2.drawContours(frame, [hull], -1, (255, 0, 0), 2)  # Blue hull

        return frame

if __name__ == "__main__":
    # Test the Overlay module
    import numpy as np

    overlay = Overlay()

    # Create a blank frame for testing
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    for state in ["SAFE", "WARNING", "DANGER"]:
        test_frame = frame.copy()
        test_frame = overlay.draw_state(test_frame, state)

        cv2.imshow(f"Overlay Test - {state}", test_frame)
        cv2.waitKey(0)

    cv2.destroyAllWindows()