import cv2
from modules.camera import Camera
from modules.hand_tracking import HandTracker
from modules.distance_logic import DistanceLogic
from modules.overlay import Overlay

def main():
    """
    Main function to run the real-time hand tracking pipeline.
    """
    # Initialize modules
    camera = Camera()
    tracker = HandTracker()
    logic = DistanceLogic()
    overlay = Overlay()

    try:
        while True:
            # Capture frame from the camera
            frame = camera.get_frame()

            # Detect hand and get contour and hull
            contour, hull = tracker.detect_hand(frame)

            # Calculate distance and determine state
            if contour is not None and hull is not None:
                # Use the centroid of the contour as the reference point
                moments = cv2.moments(contour)
                if moments['m00'] != 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    distance = logic.calculate_distance((cx, cy), (frame.shape[1] // 2, frame.shape[0] // 2))
                    state = logic.determine_state(distance)
                else:
                    state = "SAFE"
            else:
                state = "SAFE"

            # Draw overlays
            frame = tracker.draw_hand(frame, contour, hull)
            frame = overlay.draw_state(frame, state)

            # Display the frame
            cv2.imshow("Hand Tracking - Real-Time", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()