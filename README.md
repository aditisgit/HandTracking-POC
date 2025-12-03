# HandTracking-POC

## Overview
This project is a real-time hand-boundary detection system using classical computer vision techniques. It tracks a user's hand or fingertip in real time and detects when it approaches a virtual boundary on the screen. The system displays a clear "DANGER DANGER" warning overlay when the hand reaches the boundary.

## Features
- Real-time hand tracking using HSV skin segmentation, contours, and convex hull.
- Dynamic distance-based state logic:
  - **SAFE**: Hand is far from the boundary.
  - **WARNING**: Hand is approaching the boundary.
  - **DANGER**: Hand is at the boundary.
- Visual overlay system with state indicators and a flashing red warning for "DANGER".

## Requirements
- Python 3.8+
- OpenCV
- NumPy

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/aditisgit/HandTracking-POC.git
   cd HandTracking-POC
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the main script:
   ```bash
   python main.py
   ```
2. Press `q` to exit the application.

## File Structure
```
HandTracking-POC/
│
├── main.py                     # Entry point to run the pipeline
├── requirements.txt            # Dependencies for the project
├── README.md                   # Instructions for running the project
│
├── config/
│   └── config.py               # Configuration settings (thresholds, HSV ranges, etc.)
│
├── modules/
│   ├── camera.py               # Webcam feed handling
│   ├── hand_tracking.py        # Hand detection and tracking logic
│   ├── distance_logic.py       # Distance calculation and state logic
│   ├── overlay.py              # UI overlay for SAFE/WARNING/DANGER states
│
└── tests/                      # Unit tests for the modules
```

## Deployment on Lovable
1. Ensure the `requirements.txt` file is included in the repository.
2. Follow Lovable's documentation to set up the project in their sandbox environment.
3. If the webcam is unavailable in the sandbox, use a pre-recorded video feed for testing by modifying the `Camera` class in `modules/camera.py`.

## Notes
- The system is designed for CPU-only execution and achieves a target of ≥ 8 FPS.
- For best results, ensure good lighting conditions and a plain background.