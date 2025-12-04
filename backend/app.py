from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import cv2
import numpy as np
import base64
import json
import sys
import os

# Add current directory to sys.path to allow imports from main.py and its dependencies
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import HandTrackingSystem

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
# We need to go up one level from 'backend' to find 'frontend'
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, 'index.html'))

# Initialize the hand tracking system
system = HandTrackingSystem()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive frame bytes from client
            data = await websocket.receive_bytes()
            
            # Decode image
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                continue

            # Process frame to get data only
            result = system.process_frame_data(frame)
            
            # Send JSON response
            await websocket.send_json(result)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        try:
            await websocket.close()
        except:
            pass
