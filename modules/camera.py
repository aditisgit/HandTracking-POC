import cv2

class Camera:
    def __init__(self, width=640, height=480):
        """
        Initialize the camera with the given frame width and height.
        """
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def get_frame(self):
        """
        Capture a single frame from the webcam.
        Returns:
            frame (numpy.ndarray): The captured frame.
        """
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera.")
        return frame

    def release(self):
        """
        Release the camera resource.
        """
        self.cap.release()

if __name__ == "__main__":
    # Test the camera module
    camera = Camera()
    try:
        while True:
            frame = camera.get_frame()
            cv2.imshow("Webcam Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()