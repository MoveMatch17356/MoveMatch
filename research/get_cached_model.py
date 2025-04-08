import tensorflow_hub as hub
import os

def get_cached_model(model_url, cache_dir='tfhub_cache'):
    os.makedirs(cache_dir, exist_ok=True)
    os.environ['TFHUB_CACHE_DIR'] = cache_dir
    
    print(f"Checking cache for model: {model_url}")
    model = hub.load(model_url)
    print("Model loaded from cache.")
    
    return model

if __name__ == "__main__":
    # Example usage:
    model_url = "https://tfhub.dev/google/movenet/singlepose/thunder/4"
    model = get_cached_model(model_url)
