import cv2
from modules.camera import Camera
from modules.hand_tracking import HandTracker
from modules.distance_logic import DistanceLogic
from modules.overlay import Overlay
from config.config import ROI_MARGIN, DOWNSAMPLE_RATIO, CIRCLE_CENTER

def main():
    """
    Main function to run the real-time hand tracking pipeline.
    """
    # Initialize modules
    camera = Camera()
    hand_tracker = HandTracker()
    distance_logic = DistanceLogic()
    overlay = Overlay()

    try:
        while True:
            # Capture frame from the camera
            frame = camera.get_frame()

            # Detect hand and boundary point
            hand_data = hand_tracker.detect_hand(frame)
            largest_contour, hull, boundary_point = hand_data

            # Compute state
            if boundary_point is not None:
                distance = distance_logic.calculate_distance(boundary_point, CIRCLE_CENTER)
                state = distance_logic.determine_state(distance)
            else:
                state = "SAFE"

            # Draw overlays
            frame = overlay.draw_virtual_object(frame)
            frame = overlay.draw_boundary_point(frame, boundary_point, contour=largest_contour, hull=hull, debug=True)
            frame = overlay.draw_state(frame, state)

            # Display the frame
            cv2.imshow("Hand Tracking", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()