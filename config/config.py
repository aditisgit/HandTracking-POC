import cv2  # Import OpenCV for font constants

# Configuration file for the HandTracking-POC project

# HSV color range for skin detection
HSV_LOWER = (0, 30, 60)  # Lower bound of HSV for skin color
HSV_UPPER = (20, 150, 255)  # Upper bound of HSV for skin color

# Distance thresholds for state logic
THRESHOLD_SAFE = 100  # Distance above this is SAFE
THRESHOLD_WARNING = 50  # Distance between WARNING and DANGER

# Frame dimensions (optional, can be dynamically set)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Other constants
FONT = cv2.FONT_HERSHEY_SIMPLEX  # Font for overlay text
FONT_SCALE = 1
FONT_COLOR = (255, 255, 255)  # White color
LINE_THICKNESS = 2