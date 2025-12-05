# HandTracking-POC

## Overview
This project is a real-time hand-boundary detection system using classical computer vision techniques, adapted for web deployment. It tracks a user's hand or fingertip in real time and detects when it approaches a virtual boundary on the screen. The system displays a clear "DANGER DANGER" warning overlay when the hand reaches the boundary.

## Features
- **Web-based Interface**: Clean HTML/JS frontend communicating via WebSockets.
- **Real-time Processing**: Low-latency frame streaming to a FastAPI backend.
- **Classical CV**: Uses HSV skin segmentation, contours, and convex hull (no heavy ML models).
- **Robust Connectivity**: Includes watchdog timers and auto-reconnection logic for stable streaming.
- **Dynamic States**:
  - **SAFE**: Hand is far from the boundary.
  - **WARNING**: Hand is approaching the boundary.
  - **DANGER**: Hand is at the boundary.

## Project Structure
- **`backend/`**: Contains the FastAPI server (`app.py`) and core CV logic (`main.py`, `modules/`).
- **`frontend/`**: Contains the web UI (`index.html`, `styles.css`, `script.js`).
- **`legacy/`**: Archived files from previous iterations.
- **`requirements.txt`**: Python dependencies.
- **`start.bat`**: Quick start script for Windows.

## Requirements
- Python 3.8+
- OpenCV, NumPy, FastAPI, Uvicorn, Websockets

## Installation
1. Clone the repository.
2. Install dependencies:
   `ash
   pip install -r requirements.txt
   ``r

## Usage
1. **Start the Server**:
   Double-click `start.bat` or run in terminal:
   `ash
   .\start.bat
   ``r
   

2. **Open the Application**:
   Open your browser and navigate to:
   `http://localhost:8000` 

3. **Start Tracking**:
   - Allow camera access when prompted.
   - Click **Start Camera**.

## Configuration
- **CV Parameters**: Adjust detection sensitivity and thresholds in `backend/config/config.py`.
- **Frontend Settings**: Adjust FPS cap or resolution in `frontend/script.js`.
