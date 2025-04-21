import tensorflow as tf

def check_tf_gpu():
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ TensorFlow is using GPU: {gpus[0].name}")
    else:
        print("⚠️ TensorFlow is using CPU. No GPU detected.")
