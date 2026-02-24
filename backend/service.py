"""
service.py
==========
ISL Inference Service — processes uploaded video files through
MediaPipe HandLandmarker + LSTM model to predict ISL signs.

Uses the same keypoint extraction pipeline as realtime_test.py
to ensure consistency between real-time and web-based inference.
"""

import json
import os

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from tensorflow.keras.models import load_model  # type: ignore

from config import (
    MODEL_PATH,
    LABEL_MAP_PATH,
    HAND_MODEL_PATH,
    SEQUENCE_LENGTH,
    NUM_FEATURES,
    CONFIDENCE_THRESHOLD,
)


class InferenceService:
    """Singleton service that loads model once and processes video files."""

    def __init__(self):
        self.model = None
        self.actions = None
        self._load_resources()

    # ------------------------------------------------------------------ #
    #  Startup                                                            #
    # ------------------------------------------------------------------ #

    def _load_resources(self):
        """Load LSTM model and label map at server startup."""
        # ── LSTM model ──
        if os.path.isfile(MODEL_PATH):
            self.model = load_model(MODEL_PATH)
            # Warm-up inference to avoid first-request latency
            dummy = np.zeros(
                (1, SEQUENCE_LENGTH, NUM_FEATURES), dtype=np.float32
            )
            self.model.predict(dummy, verbose=0)
            print(f"[INFO] Model loaded & warmed up: {MODEL_PATH}")
        else:
            print(f"[WARNING] Model not found: {MODEL_PATH}")

        # ── Label map ──
        if os.path.isfile(LABEL_MAP_PATH):
            with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
                label_map = json.load(f)
            # Sort by index value so actions[i] matches model output index i
            self.actions = np.array(
                sorted(label_map.keys(), key=lambda k: label_map[k])
            )
            print(f"[INFO] {len(self.actions)} classes loaded from label_map.json")
        else:
            print(f"[WARNING] Label map not found: {LABEL_MAP_PATH}")

        # ── Verify hand_landmarker.task exists ──
        if not os.path.isfile(HAND_MODEL_PATH):
            print(f"[WARNING] hand_landmarker.task not found: {HAND_MODEL_PATH}")

    # ------------------------------------------------------------------ #
    #  HandLandmarker helpers                                              #
    # ------------------------------------------------------------------ #

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
        """
        Extract a flat 126-dim keypoint vector from a HandLandmarker result.
        Matches the normalized training data format.
        """
        left_hand = np.zeros(63)
        right_hand = np.zeros(63)

        if hand_result.hand_landmarks and hand_result.handedness:
            for hand_lms, handedness_list in zip(
                hand_result.hand_landmarks, hand_result.handedness
            ):
                label = (
                    handedness_list[0].category_name.lower()
                    if handedness_list
                    else ""
                )
                raw = np.array([[lm.x, lm.y, lm.z] for lm in hand_lms[:21]])

                # ✅ Normalize: Relative to wrist and scale-invariant
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

    # ------------------------------------------------------------------ #
    #  Main inference pipeline                                             #
    # ------------------------------------------------------------------ #

    def process_video(self, video_path: str) -> dict:
        """
        Process an uploaded video file and return the predicted ISL sign.

        Steps:
        1. Read all frames from the video.
        2. Run HandLandmarker on each frame to extract 126-dim keypoints.
        3. Resample the keypoint sequence to SEQUENCE_LENGTH (30) frames.
        4. Feed the sequence into the LSTM model.
        5. Return the predicted sign + confidence.
        """
        if self.model is None or self.actions is None:
            return {"error": "Model or label map not loaded. Check server logs."}

        # ── Open video ──
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": f"Could not open video file: {video_path}"}

        # ── Create HandLandmarker (per-request to avoid threading issues) ──
        hand_lm = self._create_hand_landmarker()

        sequence = []
        frame_ts_ms = 0

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert BGR → RGB for MediaPipe
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB, data=rgb
                )

                # Monotonically increasing timestamp (~30 fps)
                frame_ts_ms += 33
                hand_result = hand_lm.detect_for_video(mp_image, frame_ts_ms)

                # Extract 126-dim keypoints
                keypoints = self._extract_hand_keypoints(hand_result)
                sequence.append(keypoints)

        finally:
            cap.release()
            hand_lm.close()

        frames_processed = len(sequence)
        print(f"[INFO] Processed {frames_processed} frames from {video_path}")

        if frames_processed == 0:
            return {"error": "No frames could be read from the video."}

        # ── Resample to SEQUENCE_LENGTH frames ──
        if frames_processed >= SEQUENCE_LENGTH:
            indices = np.linspace(
                0, frames_processed - 1, SEQUENCE_LENGTH, dtype=int
            )
            final_sequence = [sequence[i] for i in indices]
        else:
            # Pad by repeating last frame
            final_sequence = list(sequence)
            while len(final_sequence) < SEQUENCE_LENGTH:
                final_sequence.append(sequence[-1])

        # ── Run LSTM prediction ──
        input_data = np.expand_dims(
            np.array(final_sequence, dtype=np.float32), axis=0
        )
        prediction = self.model.predict(input_data, verbose=0)[0]
        class_idx = int(np.argmax(prediction))
        confidence = float(prediction[class_idx])

        predicted_action = str(self.actions[class_idx])

        print(
            f"[INFO] Prediction: {predicted_action} "
            f"({confidence * 100:.1f}%)"
        )

        return {
            "prediction": predicted_action,
            "confidence": confidence,
            "all_probabilities": {
                str(action): float(prob)
                for action, prob in zip(self.actions, prediction)
            },
        }


# ── Singleton instance (loaded once when the server starts) ──
inference_service = InferenceService()
