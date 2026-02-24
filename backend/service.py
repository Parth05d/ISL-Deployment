import json
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization

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
        
        # Initial Diagnostic
        print("--- RENDER DEPLOYMENT DIAGNOSTIC ---")
        print(f"Current Working Directory: {os.getcwd()}")
        print(f"Model Path: {MODEL_PATH} | Exists: {os.path.isfile(MODEL_PATH)}")
        print(f"Label Path: {LABEL_MAP_PATH} | Exists: {os.path.isfile(LABEL_MAP_PATH)}")
        print("------------------------------------")
        
        self._load_resources()

    def _load_resources(self):
        """Fail-proof loading: Labels FIRST, then Manual architecture + Raw weights."""
        
        # 1. Load Label map FIRST to determine the output shape
        if os.path.isfile(LABEL_MAP_PATH):
            try:
                with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
                    label_map = json.load(f)
                # Sort by index to ensure correct mapping
                self.actions = np.array(sorted(label_map.keys(), key=lambda k: label_map[k]))
                print(f"[SUCCESS] Labels loaded: {len(self.actions)} classes found.")
            except Exception as e:
                print(f"[ERROR] Label map parsing failed: {e}")
        else:
            print(f"[ERROR] Label map file not found at {LABEL_MAP_PATH}")

        # Set output units based on labels, default to 21 if load failed
        num_classes = len(self.actions) if self.actions is not None else 21

        # 2. Manually define the Keras 2 compatible architecture
        # Using input_shape instead of InputLayer avoids the batch_shape crash.
        model = Sequential([
            LSTM(64, return_sequences=True, activation='relu', input_shape=(SEQUENCE_LENGTH, NUM_FEATURES)),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(128, return_sequences=True, activation='relu'),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(64, return_sequences=False, activation='relu'),
            Dropout(0.2),
            BatchNormalization(),
            
            Dense(64, activation='relu'),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])

        # 3. Load RAW weights from the H5 file
        if os.path.isfile(MODEL_PATH):
            try:
                # load_weights avoids the metadata/config check that load_model performs
                model.load_weights(MODEL_PATH)
                self.model = model
                print(f"[SUCCESS] Model weights loaded manually into memory.")
                
                # Warm-up inference
                dummy = np.zeros((1, SEQUENCE_LENGTH, NUM_FEATURES), dtype=np.float32)
                self.model.predict(dummy, verbose=0)
                print("[SUCCESS] Model warmed up and ready for inference.")
            except Exception as e:
                print(f"[CRITICAL ERROR] Weight loading failed: {e}")
                # Fallback: Try loading with by_name=True if internal naming differs
                try:
                    model.load_weights(MODEL_PATH, by_name=True)
                    self.model = model
                    print("[SUCCESS] Model weights loaded using by_name=True")
                except Exception as e2:
                    print(f"[FINAL FAIL] Could not load weights: {e2}")
        else:
            print(f"[ERROR] Model file not found at {MODEL_PATH}")

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
        """Extract flat 126-dim keypoint vector from HandLandmarker result."""
        left_hand = np.zeros(63)
        right_hand = np.zeros(63)

        if hand_result.hand_landmarks and hand_result.handedness:
            for hand_lms, handedness_list in zip(
                hand_result.hand_landmarks, hand_result.handedness
            ):
                label = handedness_list[0].category_name.lower() if handedness_list else ""
                raw = np.array([[lm.x, lm.y, lm.z] for lm in hand_lms[:21]])

                # Normalize relative to wrist
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
        """Main inference pipeline for processing video files."""
        if self.model is None or self.actions is None:
            return {"error": "Model or labels not loaded correctly."}

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
            return {"error": "No frames detected in the video."}

        # Resample to the required sequence length
        if frames_processed >= SEQUENCE_LENGTH:
            indices = np.linspace(0, frames_processed - 1, SEQUENCE_LENGTH, dtype=int)
            final_sequence = [sequence[i] for i in indices]
        else:
            final_sequence = list(sequence)
            while len(final_sequence) < SEQUENCE_LENGTH:
                final_sequence.append(sequence[-1])

        # Model Prediction
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

# Initialize singleton instance
inference_service = InferenceService()