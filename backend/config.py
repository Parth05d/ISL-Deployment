import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths
MODEL_PATH = os.path.join(BASE_DIR, "isl_lstm_model.h5")
LABEL_MAP_PATH = os.path.join(BASE_DIR, "label_map.json")
HAND_MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")

# Inference settings (must match training)
SEQUENCE_LENGTH = 30
NUM_FEATURES = 126          # 21 landmarks × 3 coords × 2 hands
CONFIDENCE_THRESHOLD = 0.60
