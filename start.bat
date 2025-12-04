@echo off
echo Starting Hand Tracking Server...
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
pause
