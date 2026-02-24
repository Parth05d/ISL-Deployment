import json
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from tensorflow.keras.models import load_model

# Import paths from config
from config import (
    MODEL_PATH,
    LABEL_MAP_PATH,
    HAND_MODEL_PATH,
    SEQUENCE_LENGTH,
    NUM_FEATURES,
    CONFIDENCE_THRESHOLD,
)

class InferenceService:
    def __init__(self):
        self.model = None
        self.actions = None
        # Diagnostic: Let's see exactly what's happening on startup
        print("--- RENDER DEPLOYMENT DIAGNOSTIC ---")
        print(f"Current Working Directory: {os.getcwd()}")
        print(f"Target Model Path: {MODEL_PATH}")
        print(f"Model File Exists? {os.path.isfile(MODEL_PATH)}")
        print(f"Label Map Path: {LABEL_MAP_PATH}")
        print(f"Label Map Exists? {os.path.isfile(LABEL_MAP_PATH)}")
        print(f"Task Path: {HAND_MODEL_PATH}")
        print(f"Task File Exists? {os.path.isfile(HAND_MODEL_PATH)}")
        
        # If files aren't found, list everything in the folder to help us debug
        if not os.path.isfile(MODEL_PATH):
            print(f"Contents of directory: {os.listdir(os.getcwd())}")
        print("------------------------------------")
        
        self._load_resources()

    def _load_resources(self):
        """Load LSTM model and label map with strict error handling."""
        # 1. Load LSTM model
        if os.path.isfile(MODEL_PATH):
            try:
                # Use compile=False to bypass potential Keras version metadata conflicts
                from tensorflow.keras.models import load_model
                print(f"[INFO] Attempting to load model from: {MODEL_PATH}")
                
                self.model = load_model(MODEL_PATH, compile=False)
                
                # Manually compile to ensure it's ready for inference
                self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
                
                # Critical: Warm-up inference
                dummy = np.zeros((1, SEQUENCE_LENGTH, NUM_FEATURES), dtype=np.float32)
                self.model.predict(dummy, verbose=0)
                print(f"[SUCCESS] Model loaded and verified.")
            except Exception as e:
                print(f"[CRITICAL ERROR] Model failed to load into memory: {e}")
                self.model = None  # Ensure it's explicitly None if it fails
        else:
            print(f"[ERROR] Model file not found at {MODEL_PATH}")

        # 2. Load Label map
        if os.path.isfile(LABEL_MAP_PATH):
            try:
                with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
                    label_map = json.load(f)
                self.actions = np.array(sorted(label_map.keys(), key=lambda k: label_map[k]))
                print(f"[SUCCESS] Labels loaded: {self.actions}")
            except Exception as e:
                print(f"[ERROR] Label map parsing failed: {e}")
        else:
            print(f"[ERROR] Label map file not found at {LABEL_MAP_PATH}")

    def _create_hand_landmarker(self):
        """Create a HandLandmarker configured for VIDEO mode."""
        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=HAND_MODEL_PATH
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        return vision.HandLandmarker.create_from_options(options)

    @staticmethod
    def _extract_hand_keypoints(hand_result) -> np.ndarray:
        left_hand = np.zeros(63)
        right_hand = np.zeros(63)

        if hand_result.hand_landmarks and hand_result.handedness:
            for hand_lms, handedness_list in zip(
                hand_result.hand_landmarks, hand_result.handedness
            ):
                label = handedness_list[0].category_name.lower() if handedness_list else ""
                raw = np.array([[lm.x, lm.y, lm.z] for lm in hand_lms[:21]])

                wrist = raw[0]
                relative = (raw - wrist)
                max_dist = np.max(np.linalg.norm(relative, axis=1))
                if max_dist > 0:
                    relative /= max_dist

                coords = relative.flatten()
                if label == "left":
                    left_hand = coords
                elif label == "right":
                    right_hand = coords

        return np.concatenate([left_hand, right_hand])

    def process_video(self, video_path: str) -> dict:
        if self.model is None or self.actions is None:
            return {"error": f"Model not loaded. Check path: {MODEL_PATH}"}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": f"Could not open video file: {video_path}"}

        hand_lm = self._create_hand_landmarker()
        sequence = []
        frame_ts_ms = 0

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                frame_ts_ms += 33
                hand_result = hand_lm.detect_for_video(mp_image, frame_ts_ms)
                keypoints = self._extract_hand_keypoints(hand_result)
                sequence.append(keypoints)
        finally:
            cap.release()
            hand_lm.close()

        frames_processed = len(sequence)
        if frames_processed == 0:
            return {"error": "No frames could be read from the video."}

        # Resample
        if frames_processed >= SEQUENCE_LENGTH:
            indices = np.linspace(0, frames_processed - 1, SEQUENCE_LENGTH, dtype=int)
            final_sequence = [sequence[i] for i in indices]
        else:
            final_sequence = list(sequence)
            while len(final_sequence) < SEQUENCE_LENGTH:
                final_sequence.append(sequence[-1])

        input_data = np.expand_dims(np.array(final_sequence, dtype=np.float32), axis=0)
        prediction = self.model.predict(input_data, verbose=0)[0]
        class_idx = int(np.argmax(prediction))
        confidence = float(prediction[class_idx])
        predicted_action = str(self.actions[class_idx])

        return {
            "prediction": predicted_action,
            "confidence": confidence,
            "all_probabilities": {str(a): float(p) for a, p in zip(self.actions, prediction)},
        }

# Singleton instance
inference_service = InferenceService()