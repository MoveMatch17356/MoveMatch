import cv2
import mediapipe as mp
import numpy as np
import argparse
import os
import json
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have PyQt5 installed
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Parse command line arguments
parser = argparse.ArgumentParser(description='Interactive 3D Pose Visualizer.')
parser.add_argument('video', type=str, help='Path to input video file.')
args = parser.parse_args()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=2)
connections = mp_pose.POSE_CONNECTIONS

output_folder = f"{os.path.splitext(os.path.basename(args.video))[0]}_3d"
os.makedirs(output_folder, exist_ok=True)
cache_file = os.path.join(output_folder, "3d_cache.json")

# Load or compute 3D keypoints
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        all_keypoints = json.load(f)
else:
    all_keypoints = []
    cap = cv2.VideoCapture(args.video)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            keypoints = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]
        else:
            keypoints = [(0, 0, 0)] * 33

        all_keypoints.append(keypoints)

    cap.release()

    with open(cache_file, 'w') as f:
        json.dump(all_keypoints, f)

# Interactive 3D Visualization
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.2)

frame_idx = 0
scat = ax.scatter([], [], [], c='r')
lines = [ax.plot([], [], [], c='b')[0] for _ in connections]

# Plotting function
def plot_frame(idx):
    ax.clear()
    ax.set_xlim([0, 1])
    ax.set_ylim([1, 0])  # invert y-axis to match image
    ax.set_zlim([-0.5, 0.5])

    keypoints = all_keypoints[idx]
    xs, ys, zs = zip(*keypoints)
    scat = ax.scatter(xs, ys, zs, c='r')

    for connection, line in zip(connections, lines):
        x_vals = [keypoints[connection[0]][0], keypoints[connection[1]][0]]
        y_vals = [keypoints[connection[0]][1], keypoints[connection[1]][1]]
        z_vals = [keypoints[connection[0]][2], keypoints[connection[1]][2]]
        ax.plot(x_vals, y_vals, z_vals, 'b')

    ax.set_title(f"Frame: {idx}")

# Initial plot
plot_frame(0)

# Slider for frames
ax_slider = plt.axes([0.25, 0.05, 0.5, 0.03])
slider = Slider(ax_slider, 'Frame', 0, len(all_keypoints)-1, valinit=0, valfmt='%0.0f')

def update(val):
    idx = int(slider.val)
    plot_frame(idx)
    fig.canvas.draw_idle()

slider.on_changed(update)

plt.show()
