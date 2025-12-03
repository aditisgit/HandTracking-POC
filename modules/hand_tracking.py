import cv2
import numpy as np
from config.config import HSV_LOWER, HSV_UPPER

class HandTracker:
    def __init__(self):
        """
        Initialize the HandTracker with pre-defined HSV ranges.
        """
        self.hsv_lower = np.array(HSV_LOWER, dtype=np.uint8)
        self.hsv_upper = np.array(HSV_UPPER, dtype=np.uint8)

    def preprocess_frame(self, frame):
        """
        Convert the frame to HSV and apply Gaussian blur.
        Args:
            frame (numpy.ndarray): Input BGR frame from the webcam.
        Returns:
            numpy.ndarray: Preprocessed HSV frame.
        """
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        return hsv

    def detect_hand(self, frame):
        """
        Detect the hand in the given frame using HSV segmentation and contours.
        Args:
            frame (numpy.ndarray): Input BGR frame from the webcam.
        Returns:
            tuple: The largest contour and the convex hull points.
        """
        hsv_frame = self.preprocess_frame(frame)
        mask = cv2.inRange(hsv_frame, self.hsv_lower, self.hsv_upper)

        # Morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, None

        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        hull = cv2.convexHull(largest_contour)

        return largest_contour, hull

    def draw_hand(self, frame, contour, hull):
        """
        Draw the detected hand contour and convex hull on the frame.
        Args:
            frame (numpy.ndarray): Input BGR frame from the webcam.
            contour (numpy.ndarray): The largest contour of the hand.
            hull (numpy.ndarray): The convex hull points of the hand.
        Returns:
            numpy.ndarray: Frame with the hand drawn.
        """
        if contour is not None and hull is not None:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)  # Green for contour
            cv2.drawContours(frame, [hull], -1, (0, 0, 255), 2)  # Red for hull
        return frame

if __name__ == "__main__":
    # Test the HandTracker module
    from modules.camera import Camera

    camera = Camera()
    tracker = HandTracker()

    try:
        while True:
            frame = camera.get_frame()
            contour, hull = tracker.detect_hand(frame)
            frame = tracker.draw_hand(frame, contour, hull)

            cv2.imshow("Hand Tracking", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()