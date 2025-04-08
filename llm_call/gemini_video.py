import google.generativeai as genai
import os
import base64

# Configure your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def encode_video_to_base64(video_path):
    """Encodes a video file to base64."""
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode("utf-8")

def analyze_sport_form(video1_path, video2_path):
    """Analyzes two sport videos and returns form improvement suggestions."""

    try:
        video1_base64 = encode_video_to_base64(video1_path)
        video2_base64 = encode_video_to_base64(video2_path)

        model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Or another suitable model

        prompt = """Analyze the two videos provided. The first video shows an individual performing a sport activity. The second video shows another individual performing the same sport activity with excellent form. 

        Provide specific and actionable feedback on how the person in the first video can improve their form to match the person in the second video. Focus on key differences in posture, movement, and technique. Be detailed.

        Video 1: [Video data]
        Video 2: [Video data]

        Provide the answer in a list of improvements."""

        response = model.generate_content(
            [
                prompt,
                {"mime_type": "video/mp4", "data": video1_base64},
                {"mime_type": "video/mp4", "data": video2_base64},
            ],
            stream=False,
        )

        return response.text

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage (replace with your video file paths)
video1_path = "../smokescreen_test/blaise.mp4"  # Replace with the path to your first video
video2_path = "../smokescreen_test/federer.mp4"  # Replace with the path to your second video

# Ensure the videos are in a supported format like mp4.
if not os.path.exists(video1_path) or not os.path.exists(video2_path):
    print("Error: Video files not found. Please provide valid file paths.")
else:
    analysis_result = analyze_sport_form(video1_path, video2_path)
    print(analysis_result)
