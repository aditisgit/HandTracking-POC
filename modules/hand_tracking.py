import cv2
import numpy as np
from config.config import CIRCLE_CENTER, DOWNSAMPLE_RATIO, HSV_LOWER, HSV_UPPER, ROI_MARGIN, SMOOTHING_WINDOW_SIZE, SMOOTHING_ALPHA, MAX_DISPLACEMENT
from modules.smoothing_utils import PointSmoother
import threading

class HandTracker:
    def __init__(self):
        """
        Initialize the HandTracker with pre-defined HSV ranges.
        """
        self.hsv_lower = np.array(HSV_LOWER, dtype=np.uint8)
        self.hsv_upper = np.array(HSV_UPPER, dtype=np.uint8)
        self.smoother = PointSmoother(window_size=SMOOTHING_WINDOW_SIZE, alpha=SMOOTHING_ALPHA, max_displacement=MAX_DISPLACEMENT)
        self.roi = None  # Region of interest for tracking
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))  # Cached kernel

    def preprocess_frame(self, frame):
        """
        Preprocess the frame with optional ROI and downsampling.
        Returns:
            hsv_frame: The processed HSV frame.
            roi_offset: (x, y) offset of the ROI in global coordinates.
        """
        roi_offset = (0, 0)
        
        if self.roi is not None:
            x, y, w, h = self.roi
            # Ensure ROI is within frame bounds
            h_frame, w_frame = frame.shape[:2]
            x = max(0, x)
            y = max(0, y)
            w = min(w, w_frame - x)
            h = min(h, h_frame - y)
            
            if w > 0 and h > 0:
                frame = frame[y:y+h, x:x+w]
                roi_offset = (x, y)
            else:
                self.roi = None # Reset invalid ROI

        # Downsample for faster processing
        frame = cv2.resize(frame, None, fx=DOWNSAMPLE_RATIO, fy=DOWNSAMPLE_RATIO, interpolation=cv2.INTER_LINEAR)
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        return hsv, roi_offset

    def transform_to_global(self, contour, roi_offset):
        """
        Transform contour points from local (downsampled + ROI) to global coordinates.
        """
        if contour is None:
            return None
        
        # Scale up
        scale = 1.0 / DOWNSAMPLE_RATIO
        contour = contour.astype(np.float32) * scale
        
        # Add ROI offset
        contour[:, :, 0] += roi_offset[0]
        contour[:, :, 1] += roi_offset[1]
        
        return np.round(contour).astype(np.int32)

    def detect_hand(self, frame):
        """
        Detect the hand and update the ROI for tracking.
        """
        hsv_frame, roi_offset = self.preprocess_frame(frame)
        mask = cv2.inRange(hsv_frame, self.hsv_lower, self.hsv_upper)

        # Morphological operations
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            self.roi = None  # Reset ROI if no hand is detected
            self.smoother.smooth(None) # Reset smoother
            return None, None, None

        # Filter contours by area to remove noise
        valid_contours = [c for c in contours if cv2.contourArea(c) > 3000]

        if not valid_contours:
            self.roi = None
            self.smoother.smooth(None) # Reset smoother
            return None, None, None

        # Find the largest contour
        largest_contour = max(valid_contours, key=cv2.contourArea)
        
        # Check if contour touches the ROI border
        if self.roi is not None:
            x, y, w, h = 0, 0, hsv_frame.shape[1], hsv_frame.shape[0]
            x_min, y_min = np.min(largest_contour[:, 0, :], axis=0)
            x_max, y_max = np.max(largest_contour[:, 0, :], axis=0)
            
            # If touching border, reset ROI for next frame to ensure full capture
            if x_min <= 1 or y_min <= 1 or x_max >= w - 2 or y_max >= h - 2:
                self.roi = None

        # Transform contour to global coordinates immediately
        global_contour = self.transform_to_global(largest_contour, roi_offset)
        
        # Compute hull in global coordinates
        hull = cv2.convexHull(global_contour)

        # Compute the closest boundary point (using global contour)
        closest_point = self.get_closest_boundary_point(global_contour)
        
        # Smooth the point
        smoothed_point = self.smoother.smooth(closest_point)

        # Update ROI based on GLOBAL contour
        x, y, w, h = cv2.boundingRect(global_contour)
        self.roi = (
            max(0, x - ROI_MARGIN), 
            max(0, y - ROI_MARGIN), 
            w + 2 * ROI_MARGIN, 
            h + 2 * ROI_MARGIN
        )

        return global_contour, hull, smoothed_point

    def get_closest_boundary_point(self, contour):
        """
        Compute the closest point on the boundary to the virtual object.
        Contour is expected to be in GLOBAL coordinates.
        """
        if contour is None:
            return None

        # Calculate distances to the circle center
        # contour is shape (N, 1, 2)
        points = contour[:, 0, :]
        diff = points - np.array(CIRCLE_CENTER)
        distances = np.linalg.norm(diff, axis=1)
        
        min_idx = np.argmin(distances)
        return tuple(points[min_idx])

    def get_centroid(self, contour):
        """
        Compute the centroid of the given contour.
        """
        if contour is None:
            return None
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return None
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        return (cx, cy)

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