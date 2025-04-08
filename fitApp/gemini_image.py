import google.generativeai as genai
import os
import base64

# Configure your API key
#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key="AIzaSyAhsPu0-rMa5-uIsCS3Vs-7veLGJha0Sso")

def encode_image_to_base64(image_path):
    """Encodes an image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_sport_form_images(image1_path, image2_path):
    """Analyzes two sport images and returns form improvement suggestions."""

    try:
        image1_base64 = encode_image_to_base64(image1_path)
        image2_base64 = encode_image_to_base64(image2_path)

        model = genai.GenerativeModel('gemini-1.5-pro-vision')  # Or another suitable model

        prompt = """Analyze the two images provided. The first image shows an individual performing a sport activity. The second image shows another individual performing the same sport activity with excellent form.

        Provide specific and actionable feedback on how the person in the first image can improve their form to match the person in the second image. Focus on key differences in posture, movement, and technique. Be detailed.

        Image 1: [Image data]
        Image 2: [Image data]

        Provide the answer in a list of improvements."""

        response = model.generate_content(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": image1_base64}, #or image/png, etc.
                {"mime_type": "image/jpeg", "data": image2_base64},
            ],
            stream=False,
        )

        return response.text

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage (replace with your image file paths)
image1_path = "image1.jpg"  # Replace with the path to your first image
image2_path = "image2.jpg"  # Replace with the path to your second image

# Ensure the images are in a supported format like jpg or png.
if not os.path.exists(image1_path) or not os.path.exists(image2_path):
    print("Error: Image files not found. Please provide valid file paths.")
else:
    analysis_result = analyze_sport_form_images(image1_path, image2_path)
    print(analysis_result)
