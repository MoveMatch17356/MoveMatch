import google.generativeai as genai
import os
import base64
from typing import List, Dict

# Configure your API key
genai.configure(api_key="AIzaSyAhsPu0-rMa5-uIsCS3Vs-7veLGJha0Sso")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_athlete_feedback(
    sport: str,
    technique: str,
    joints: List[str],
    plot_paths: Dict[str, Dict[str, str]]
) -> str:
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        prompt = (
            f"You are a data-driven athletics coach helping your {sport} athlete to change their {technique}.\n\n"
            "You are given a video of your athlete's current technique, and a comparison video that your athlete "
            "wants to change their technique to look more like.\n\n"
            "You are also given some informative graphs relating to the angles of joints of your athlete and the comparison "
            f"athlete during their {technique}s over time.\n\n"
            # "The DTW plot represents the dynamic-time warping mapping of the athlete's technique to the comparison athlete's technique. "
            # "The mapping shows which parts of the technique are slower or faster in your athlete compared to the comparison.\n\n"
            "For each of the following joints:\n\n"
        )

        # Add joint names
        for joint in joints:
            prompt += f" - {joint}\n"

        prompt += (
            "\nYou are given plots of their angles over time.\n\n"
            "Please give some simple, actionable advice to your athlete on how to change their technique to look more like that of the comparison athlete. "
            "Do not mention technical terms or anything under the hood. You are communicating to an athlete, not a statistician. "
            "Make sure your response is given as a list of actionable bullet points.\n\n"
            "Good luck!"
        )

        print("Prompt: \n\n")
        print(prompt)

        # Collect image data for Gemini
        images = []
        for joint in joints:
            # for kind in ["raw_plot", "dtw_path_plot", "aligned_plot"]:
            # for kind in ["dtw_path_plot", "aligned_plot"]:
            for kind in ["raw_plot"]:
                path = plot_paths[joint][kind]
                images.append({
                    "mime_type": "image/png" if path.endswith(".png") else "image/jpeg",
                    "data": encode_image_to_base64(path)
                })

        print("Generating content...")
        response = model.generate_content([prompt] + images, stream=False)
        print("Generated content!\n")

        print("Response:")
        print(response.text)

        return response.text

    except Exception as e:
        return f"An error occurred while generating feedback: {e}"
