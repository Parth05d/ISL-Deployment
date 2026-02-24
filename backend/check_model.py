import tensorflow as tf
import os

# Path to your original/working-ish model
model_path = r"d:\Futurrizon\Sign-language-images\frontend_ISL\backend\isl_lstm_model copy.h5"

if os.path.exists(model_path):
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        print("\n--- MODEL SUMMARY ---")
        model.summary()
        print("\n--- WEIGHT ARRAYS ---")
        print(f"Total weight arrays: {len(model.get_weights())}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File not found. Check the path in the script.")