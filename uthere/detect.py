"""Camera capture and face detection for user presence."""

import cv2


def detect_user_presence(warmup_frames: int = 10) -> bool:
    """Capture a frame from the webcam and detect if a face is present.

    Takes several warmup frames to let the camera adjust exposure,
    then runs Haar cascade face detection on the final frame.

    Returns True if at least one face is detected.
    Raises RuntimeError if the camera cannot be opened or read.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError(
            "Cannot open camera. Check that no other app is using it "
            "and that Terminal has camera permission in System Settings > Privacy & Security > Camera."
        )

    try:
        # Warm up - let auto-exposure settle
        for _ in range(warmup_frames):
            cap.read()

        ret, frame = cap.read()
        if not ret or frame is None:
            raise RuntimeError("Camera opened but failed to capture a frame.")
    finally:
        cap.release()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )

    return len(faces) > 0
