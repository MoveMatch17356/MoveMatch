

import google.generativeai as genai
import numpy as np
import os

# Configure your API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def generate_feedback(video1_data, video2_data):
    """
    Generates textual feedback comparing two videos based on joint angle data.

    Args:
        video1_data: A string representing the joint angle data for video 1.
        video2_data: A string representing the joint angle data for video 2.

    Returns:
        A string containing the generated feedback.
    """

    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    prompt = f"""
    Analyze the following joint angle data from two videos of a person kicking a soccer ball. 
    Provide feedback to the person in video1 on how to improve their form to match video2 more closely.

    Video 1 Joint Angle Data (Time (ms), Hip Angle (°), Knee Angle (°), Ankle Angle (°)):
    {video1_data}

    Video 2 Joint Angle Data (Time (ms), Hip Angle (°), Knee Angle (°), Ankle Angle (°)):
    {video2_data}

    Focus on the following aspects:
    - Differences in hip, knee, and ankle angles over time.
    - Timing and range of motion.
    - Potential areas for improvement in video 1's technique.

    Give specific and actionable feedback.
    """

    response = model.generate_content(prompt)
    return response.text

# Example data (replace with your actual data)
video1_data = """
Time (ms), Hip Angle (°), Knee Angle (°), Ankle Angle (°)
0, 5.2, 8.1, 4.0
10, 4.9, 7.8, 3.8
20, 4.5, 7.2, 3.5
30, 4.1, 6.8, 3.2
40, 3.6, 6.1, 2.9
50, 3.2, 5.8, 2.5
"""

video2_data = """
Time (ms), Hip Angle (°), Knee Angle (°), Ankle Angle (°)
0, 6.0, 9.0, 4.5
10, 5.8, 8.8, 4.3
20, 5.5, 8.2, 4.0
30, 5.2, 7.9, 3.8
40, 4.9, 7.5, 3.5
50, 4.6, 7.2, 3.2
"""

# # Generate and print the feedback
# feedback = generate_feedback(video1_data, video2_data)
# print(feedback)


def generate_image_feedback(image1_data, image2_data):
    """
    Generates textual feedback comparing two images based on keypoint coordinates.

    Args:
        image1_data: A list of dictionaries representing keypoint coordinates for image 1.
        image2_data: A list of dictionaries representing keypoint coordinates for image 2.

    Returns:
        A string containing the generated feedback, or None if an error occurs.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        def format_keypoints(data):
            formatted_data = ""
            for point in data:
                for key, value in point.items():
                    if key != 'confidence_score':
                        formatted_data += f"{key}: x={value[0]:.4f}, y={value[1]:.4f}\n"
            return formatted_data

        image1_formatted = format_keypoints(image1_data)
        image2_formatted = format_keypoints(image2_data)

        prompt = f"""
        Analyze the following keypoint coordinates from two images of a person kicking a soccer ball. 
        Provide a short paragraph of overall feedback to the person in image1 on how to modify their form to match image2 more closely.

        Image 1 Keypoint Coordinates:
        {image1_formatted}

        Image 2 Keypoint Coordinates:
        {image2_formatted}

        Focus on the relative positions of the body parts (shoulders, elbows, wrists, hips, knees, ankles).
        Give overall, actionable feedback on how the person in image1 can adjust their posture to better match image2.
        Do not mention specific x,y coordinates.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example keypoint data (replace with your actual data)
image1_data = [
    {'nose': np.array([0.2948, 0.5789], dtype=np.float32)},
    {'left_eye': np.array([0.2784, 0.5914], dtype=np.float32)},
    {'right_eye': np.array([0.2768, 0.5629], dtype=np.float32)},
    {'left_shoulder': np.array([0.3220, 0.6247], dtype=np.float32)},
    {'right_shoulder': np.array([0.3039, 0.4858], dtype=np.float32)},
    {'left_hip': np.array([0.4919, 0.5837], dtype=np.float32)},
    {'right_hip': np.array([0.4967, 0.4940], dtype=np.float32)},
    {'left_knee': np.array([0.6256, 0.5730], dtype=np.float32)},
    {'right_knee': np.array([0.6426, 0.5260], dtype=np.float32)},
    {'left_ankle': np.array([0.7089, 0.6324], dtype=np.float32)},
    {'right_ankle': np.array([0.6910, 0.6094], dtype=np.float32)}
]

image2_data = [
    {'nose': np.array([0.3000, 0.5700], dtype=np.float32)},
    {'left_eye': np.array([0.2850, 0.5800], dtype=np.float32)},
    {'right_eye': np.array([0.2800, 0.5500], dtype=np.float32)},
    {'left_shoulder': np.array([0.3300, 0.6100], dtype=np.float32)},
    {'right_shoulder': np.array([0.3100, 0.4700], dtype=np.float32)},
    {'left_hip': np.array([0.5000, 0.5700], dtype=np.float32)},
    {'right_hip': np.array([0.5050, 0.4800], dtype=np.float32)},
    {'left_knee': np.array([0.6400, 0.5600], dtype=np.float32)},
    {'right_knee': np.array([0.6500, 0.5100], dtype=np.float32)},
    {'left_ankle': np.array([0.7200, 0.6200], dtype=np.float32)},
    {'right_ankle': np.array([0.7000, 0.5900], dtype=np.float32)}
]

# Generate and print the feedback
feedback = generate_image_feedback(image1_data, image2_data)
if feedback:
    print(feedback)