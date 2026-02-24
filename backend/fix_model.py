import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import numpy as np

import os

base_dir = r"d:\Futurrizon\Sign-language-images\frontend_ISL\backend"

# Load the original model ignoring the bad config
try:
    print("Loading existing Keras 3 model...")
    # This will likely fail with the same issue, but we can try loading weights only if it worked
    model = tf.keras.models.load_model(os.path.join(base_dir, 'isl_lstm_model.h5'), compile=False)
    weights = model.get_weights()
    print("Loaded weights successfully via full load.")
except Exception as e:
    print(f"Full load failed: {e}. Trying to build architecture and load weights manually...")
    
    # 1. Build the exact same architecture but using Keras 2 style layers
    # Based on standard shape: (30 frames, 126 keypoints)
    model = Sequential()
    
    # Keras 2 compatible input layer definition
    model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(30, 126)))
    model.add(LSTM(128, return_sequences=True, activation='relu'))
    model.add(LSTM(64, return_sequences=False, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    # Change '10' below if the number of classes in label_map.json is different
    import json
    with open(os.path.join(base_dir, 'label_map.json'), 'r') as f:
        labels = json.load(f)
    num_classes = len(labels)
    model.add(Dense(num_classes, activation='softmax'))
    
    # 2. Extract weights manually from the h5 file
    import h5py
    with h5py.File(os.path.join(base_dir, 'isl_lstm_model copy.h5'), 'r') as f:
        print("Extracting weights from h5 file...")
        model.load_weights(os.path.join(base_dir, 'isl_lstm_model copy.h5'), by_name=True)

print("Saving model in deep backward compatible Keras format...")
# Save the model down to the h5 format so the older Keras deployment can read it flawlessly
model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

# Overwrite the original
model.save(os.path.join(base_dir, 'isl_lstm_model.h5'))
print("Model re-saved successfully! Please push to github.")
