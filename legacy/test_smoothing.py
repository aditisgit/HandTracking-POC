import cv2
import numpy as np
from smoothing_utils import PointSmoother

def compute_jitter(points):
    """Compute mean frame-to-frame displacement."""
    displacements = [
        np.linalg.norm(np.array(points[i]) - np.array(points[i - 1]))
        for i in range(1, len(points))
    ]
    return np.mean(displacements) if displacements else 0

def main():
    video_path = "test_video.mp4"  # Replace with your test video path
    cap = cv2.VideoCapture(video_path)

    smoother = PointSmoother(ema_alpha=0.4, median_N=5, max_displacement=100)
    raw_points = []
    smoothed_points = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Simulate raw point detection (e.g., random points for testing)
        raw_point = (np.random.randint(0, 640), np.random.randint(0, 360))
        smoothed_point = smoother.update(raw_point)

        raw_points.append(raw_point)
        smoothed_points.append(smoothed_point if smoothed_point else raw_point)

    cap.release()

    # Compute jitter
    raw_jitter = compute_jitter(raw_points)
    smoothed_jitter = compute_jitter(smoothed_points)

    print(f"Raw jitter: {raw_jitter:.2f}")
    print(f"Smoothed jitter: {smoothed_jitter:.2f}")

if __name__ == "__main__":
    main()