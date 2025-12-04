import cv2
from modules.hand_tracking import HandTracker
from modules.distance_logic import DistanceLogic
from modules.overlay import Overlay
from config.config import CIRCLE_CENTER

class HandTrackingSystem:
    def __init__(self):
        """
        Initialize the hand tracking system components.
        """
        self.hand_tracker = HandTracker()
        self.distance_logic = DistanceLogic()
        self.overlay = Overlay()

    def process_frame(self, frame):
        """
        Process a single frame: detect hand, compute state, draw overlays.
        Args:
            frame (numpy.ndarray): Input BGR frame.
        Returns:
            tuple: (processed_frame, state)
        """
        # Detect hand and boundary point
        hand_data = self.hand_tracker.detect_hand(frame)
        largest_contour, hull, boundary_point = hand_data

        # Reset ROI if tracking is lost (boundary_point is None)
        if boundary_point is None:
            self.hand_tracker.roi = None

        # Compute state
        if boundary_point is not None:
            distance = self.distance_logic.calculate_distance(boundary_point, CIRCLE_CENTER)
            state = self.distance_logic.determine_state(distance)
        else:
            state = "SAFE"

        # Draw overlays
        frame = self.overlay.draw_virtual_object(frame)
        frame = self.overlay.draw_boundary_point(frame, boundary_point, contour=largest_contour, hull=hull, debug=True)
        frame = self.overlay.draw_state(frame, state)

        return frame, state

def main():
    """
    Main function to run the real-time hand tracking pipeline locally.
    """
    from modules.camera import Camera
    
    # Initialize modules
    camera = Camera()
    system = HandTrackingSystem()

    try:
        while True:
            # Capture frame from the camera
            frame = camera.get_frame()

            # Process frame
            processed_frame, state = system.process_frame(frame)

            # Display the frame
            cv2.imshow("Hand Tracking", processed_frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
