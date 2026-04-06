"""Camera capture and face detection for user presence."""

import os
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

MODEL_DIR = os.path.expanduser("~/.cache/uthere")
MODEL_PATH = os.path.join(MODEL_DIR, "blaze_face_short_range.tflite")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite"


def _ensure_model() -> str:
    """Download the BlazeFace model if not already cached."""
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_DIR, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def detect_user_presence(warmup_frames: int = 10, check_frames: int = 3) -> bool:
    """Capture from the webcam and detect if a face is present.

    Uses MediaPipe BlazeFace (a lightweight neural network) for much better
    accuracy than Haar cascades -- handles glasses, angles, and varied lighting.

    Takes several warmup frames to let the camera adjust exposure,
    then checks multiple frames -- returns True if ANY frame contains a face.

    Raises RuntimeError if the camera cannot be opened or read.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError(
            "Cannot open camera. Check that no other app is using it "
            "and that Terminal has camera permission in System Settings > Privacy & Security > Camera."
        )

    options = vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=_ensure_model()),
        min_detection_confidence=0.3,
    )
    detector = vision.FaceDetector.create_from_options(options)

    try:
        # Warm up - let auto-exposure settle
        for _ in range(warmup_frames):
            cap.read()

        # Check multiple frames -- any face in any frame = present
        for _ in range(check_frames):
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect(mp_image)
            if result.detections:
                return True
    finally:
        cap.release()
        detector.close()

    return False
