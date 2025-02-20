import cv2
import mediapipe as mp
import sys
import os
import numpy as np

# Check if input video path is provided
if len(sys.argv) < 2:
    print("Usage: python pose_estimation.py <input_video_path>")
    sys.exit(1)

# Get input video path from the command line
input_path = sys.argv[1]

# Verify if the file exists
if not os.path.exists(input_path):
    print(f"Error: File '{input_path}' not found.")
    sys.exit(1)

# Generate output paths by inserting '_pose' and '_pose_side_by_side' before the file extension
base_name, ext = os.path.splitext(input_path)
pose_output_path = f"{base_name}_pose{ext}"
combined_output_path = f"{base_name}_pose_side_by_side{ext}"

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Open the input video file
cap = cv2.VideoCapture(input_path)

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter objects for side-by-side and pose-only outputs
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for .avi files
combined_out = cv2.VideoWriter(combined_output_path, fourcc, fps, (frame_width * 2, frame_height))
pose_out = cv2.VideoWriter(pose_output_path, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Keep the original frame for side-by-side display
    original_frame = frame.copy()

    # Convert the BGR image to RGB for MediaPipe processing
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and detect pose
    results = pose.process(image_rgb)

    # Draw the pose annotation on the image
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Combine the original and pose frames side by side
    combined_frame = np.hstack((original_frame, frame))

    # Write the combined frame and pose-only frame to the output videos
    combined_out.write(combined_frame)
    pose_out.write(frame)

# Release resources
cap.release()
combined_out.release()
pose_out.release()

print(f"Combined video saved as {combined_output_path}")
print(f"Pose-only video saved as {pose_output_path}")
