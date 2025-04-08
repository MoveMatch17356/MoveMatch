from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Optional
import base64
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

print("API key: ", api_key)

# Optional: if you use GPT-4 Vision
USE_IMAGE_MODEL = True

def encode_image_base64(path: str) -> str:
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def request_ai_feedback(
    joint_name: str,
    angles1: List[Optional[float]],
    angles2: List[Optional[float]],
    raw_plot_path: str,
    dtw_plot_path: str,
    aligned_plot_path: str
):
    print("\n🧠 Requesting AI feedback based on joint angle data and DTW alignment plots...")

    if USE_IMAGE_MODEL:
        raw_img = encode_image_base64(raw_plot_path)
        dtw_img = encode_image_base64(dtw_plot_path)
        aligned_img = encode_image_base64(aligned_plot_path)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Compare these plots and give feedback."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{raw_img}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{dtw_img}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{aligned_img}"}},
                    ],
                }
            ],
            max_tokens=800,
        )

    else:
        prompt = f"""
You're a motion coach. You have time-aligned angle data from two videos:
angles_amateur = {angles1[:120]}
angles_pro_aligned = {angles2[:120]}

The joint being analyzed is '{joint_name}'.
Provide coaching feedback on how the amateur can improve, based on the motion differences.
Consider tempo, transitions, and joint control.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )

    print("\n--- AI Coaching Advice ---\n")
    print(response.choices[0].message.content)