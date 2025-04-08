import cv2
import mediapipe as mp
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import json
import time 

from get_cached_model import get_cached_model

# Joint mapping
joint_map = {
    'left_elbow': [11, 13, 15],
    'right_elbow': [12, 14, 16],
    'left_knee': [23, 25, 27],
    'right_knee': [24, 26, 28],
    'left_hip': [11, 23, 25],
    'right_hip': [12, 24, 26],
    'left_shoulder': [13, 11, 23],
    'right_shoulder': [14, 12, 24]
}

# Parse command line arguments
parser = argparse.ArgumentParser(description='Pose estimation with selectable methods.')
parser.add_argument('video', type=str, help='Path to input video file.')
parser.add_argument('--method', type=str, default='mediapipe', choices=['mediapipe', 'movenet'], help='Pose estimation method.')
parser.add_argument('--joints', nargs='+', default=list(joint_map.keys()), help='List of joints to measure angles.')
args = parser.parse_args()

POSE_CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS

output_folder = f"{os.path.splitext(os.path.basename(args.video))[0]}_2d"
os.makedirs(output_folder, exist_ok=True)

cache_file = os.path.join(output_folder, "cache.json")
output_video = os.path.join(output_folder, f"output_{args.method}.mp4")


# Common interface
class PoseEstimator:
    def estimate_pose(self, image):
        pass

# MediaPipe implementation
class MediaPipePoseEstimator(PoseEstimator):
    def __init__(self):
        self.pose = mp.solutions.pose.Pose()

    def estimate_pose(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        keypoints = {}
        if results.pose_landmarks:
            keypoints = {i: (lm.x, lm.y) for i, lm in enumerate(results.pose_landmarks.landmark)}
        return keypoints

# MoveNet implementation
class MoveNetPoseEstimator(PoseEstimator):
    def __init__(self):
        model_url = "https://tfhub.dev/google/movenet/singlepose/thunder/4"
        model = get_cached_model(model_url)
        self.movenet = model.signatures['serving_default']

    def estimate_pose(self, image):
        img_resized = cv2.resize(image, (256, 256)).astype(np.int32)
        tensor = tf.convert_to_tensor(img_resized[np.newaxis, ...])
        outputs = self.movenet(tensor)['output_0'].numpy().reshape(17, 3)
        keypoints = {i: (y, x) for i, (y, x, _) in enumerate(outputs)}
        return keypoints



# Angle calculation
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return angle if angle <= 180 else 360-angle

cache_file = os.path.join(output_folder, "cache.json")
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        cache = json.load(f)
else:
    cache = {}

# Select estimator
if args.method == 'mediapipe':
    estimator = MediaPipePoseEstimator()
else:
    estimator = MoveNetPoseEstimator()

cap = cv2.VideoCapture(args.video)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, 30, (width, height))

# Initialize timing variables
total_time = 0
frame_count = 0
frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if str(frame_idx) in cache:
        keypoints = cache[str(frame_idx)]
    else:
        start_time = time.time()  # start timer
        keypoints = estimator.estimate_pose(frame)
        end_time = time.time()  # end timer

        elapsed = end_time - start_time
        total_time += elapsed
        frame_count += 1

        cache[str(frame_idx)] = keypoints

    # Draw skeleton
    for connection in POSE_CONNECTIONS:
        pt1, pt2 = connection
        if pt1 in keypoints and pt2 in keypoints:
            x1, y1 = int(keypoints[pt1][0]*width), int(keypoints[pt1][1]*height)
            x2, y2 = int(keypoints[pt2][0]*width), int(keypoints[pt2][1]*height)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

    y_offset = 30
    for joint in args.joints:
        if joint in joint_map:
            ids = joint_map[joint]
            if all(id in keypoints for id in ids):
                points = [(int(keypoints[id][0]*width), int(keypoints[id][1]*height)) for id in ids]
                angle = calculate_angle(*points)

                # Draw lines and arc
                cv2.line(frame, points[0], points[1], (0, 255, 0), 2)
                cv2.line(frame, points[1], points[2], (0, 255, 0), 2)
                cv2.circle(frame, points[1], 5, (0, 0, 255), -1)

                # Text at joint
                cv2.putText(frame, f'{int(angle)}', points[1], cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

                # Top-left corner labels
                cv2.putText(frame, f'{joint}: {int(angle)} deg', (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                y_offset += 30

    out.write(frame)
    frame_idx += 1

cap.release()
out.release()

# Saving cache at the end
with open(cache_file, 'w') as f:
    json.dump(cache, f)

# Plot angles for each joint
angle_history = {joint: [] for joint in args.joints}

for idx in range(frame_idx):
    keypoints = cache[str(idx)]
    for joint in args.joints:
        if joint in joint_map:
            ids = joint_map[joint]
            if all(str(id) in keypoints or id in keypoints for id in ids):
                points = [(keypoints[str(id)] if str(id) in keypoints else keypoints[id]) for id in ids]
                points_px = [(x*width, y*height) for x, y in points]
                angle = calculate_angle(*points_px)
                
                angle_history[joint].append(angle)
            else:
                angle_history[joint].append(None)

# Create vertically stacked plots
fig, axs = plt.subplots(len(args.joints), 1, figsize=(10, 4 * len(args.joints)), sharex=True)

if len(args.joints) == 1:
    axs = [axs]

def smooth_angles(angles, window_size=5):
    smoothed = np.convolve(
        angles, np.ones(window_size) / window_size, mode='same')
    return smoothed

for ax, joint in zip(axs, args.joints):
    angles = np.array(angle_history[joint])
    angles = np.where(np.isnan(angles), np.nanmean(angles), angles)  # fill missing values if any
    smoothed_angles = smooth_angles(angles)

    ax.plot(smoothed_angles, label=f'{joint} angle (smoothed)', color='blue')
    ax.plot(angles, alpha=0.3, color='orange', linestyle='--', label='original')
    ax.set_title(f'{joint.capitalize()} Angle Over Time (Smoothed)')
    ax.set_ylabel('Angle (degrees)')
    ax.grid(True)
    ax.legend()

axs[-1].set_xlabel('Frame Number')

plot_path = os.path.join(output_folder, "joint_angles_smoothed.png")
plt.tight_layout()
plt.savefig(plot_path)
plt.close()


if frame_count > 0:
    average_time = total_time / frame_count
    print(f"Processed {frame_count} frames. Average pose estimation time per frame: {average_time:.4f} seconds. Total time: {total_time:.4f}")
else:
    print("All frames loaded from cache, no timing data calculated.")

print(f"Saved output as '{output_video}'")
