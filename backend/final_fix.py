import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
import os

# Paths
base_dir = r"d:\Futurrizon\Sign-language-images\frontend_ISL\backend"
old_model_path = os.path.join(base_dir, 'isl_lstm_model copy.h5')
new_model_path = os.path.join(base_dir, 'isl_lstm_model.h5')

print("Building exact architecture for Keras 2...")

model = Sequential([
    # Layer 1
    LSTM(64, return_sequences=True, activation='relu', input_shape=(30, 126)),
    Dropout(0.2), # Dropout doesn't have weights, but it's part of the structure
    BatchNormalization(),
    
    # Layer 2
    LSTM(128, return_sequences=True, activation='relu'),
    Dropout(0.2),
    BatchNormalization(),
    
    # Layer 3
    LSTM(64, return_sequences=False, activation='relu'),
    Dropout(0.2),
    BatchNormalization(),
    
    # Dense Layers
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(21, activation='softmax') # Your summary showed 21 classes
])

print("Loading weights from original model...")
try:
    # Load old model to grab weights
    old_model = tf.keras.models.load_model(old_model_path, compile=False)
    
    # Transfer weights
    model.set_weights(old_model.get_weights())
    print("SUCCESS: All 27 weight arrays transferred perfectly!")
    
    # Save in Legacy H5 format
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.save(new_model_path, save_format='h5')
    
    print(f"--- DONE ---")
    print(f"Fixed model saved: {new_model_path}")
    print(f"New size: {os.path.getsize(new_model_path) // 1024} KB")

except Exception as e:
    print(f"FAILED: {e}")