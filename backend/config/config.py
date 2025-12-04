import cv2  # Import OpenCV for font constants

# Configuration file for the HandTracking-POC project

# HSV color range for skin detection
HSV_LOWER = (0, 40, 60)  # Increased Saturation/Value to reject pale background
HSV_UPPER = (20, 255, 255)  # Upper bound of HSV for skin color

# YCrCb color range for skin detection (Additional filter)
YCRCB_LOWER = (0, 135, 85)
YCRCB_UPPER = (255, 180, 135)

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

# Smoothing parameters
SMOOTHING_WINDOW_SIZE = 3
SMOOTHING_ALPHA = 0.6
MAX_DISPLACEMENT = 100

# Circle parameters
CIRCLE_CENTER = (320, 240)  # Center of the virtual object
CIRCLE_RADIUS = 50
WARNING_BAND = 50

# Debounce parameters
DEBOUNCE_FRAMES = 3

# ROI and performance parameters
ROI_MARGIN = 100  # Margin around the detected hand for ROI tracking
DOWNSAMPLE_RATIO = 1.0  # Downsample ratio for mask processing

# Noise reduction parameters
MIN_AREA = 5000  # Minimum contour area to be considered a hand
MORPH_KERNEL = (7, 7)  # Kernel size for morphological operations
MASK_CONFIDENCE_MIN = 0.5  # Minimum confidence for mask validity
USE_MOTION_FALLBACK = True  # Enable motion-based fallback mask