import cv2
from typing import List, Optional, Dict
from utils.types import Frame, Point3D
from processing.angle_analysis import JOINT_MAP, calculate_angle

# Skeleton lines for MediaPipe (subset just to show basic structure)
SKELETON_CONNECTIONS = [
    (11, 13), (13, 15),  # left arm
    (12, 14), (14, 16),  # right arm
    (11, 12),            # shoulders
    (23, 24),            # hips
    (11, 23), (12, 24),  # torso sides
    (23, 25), (25, 27),  # left leg
    (24, 26), (26, 28)   # right leg
]

def annotate_video(
    original_video_path: str,
    output_path: str,
    frames: List[Frame],
    selected_joints: Optional[List[str]] = None,
    show_angles: bool = True
):
    cap = cv2.VideoCapture(original_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for idx, frame_data in enumerate(frames):
        ret, frame = cap.read()
        if not ret:
            break

        keypoints = frame_data.pose.keypoints

        # Draw skeleton
        for i1, i2 in SKELETON_CONNECTIONS:
            p1 = keypoints[i1]
            p2 = keypoints[i2]
            if p1 and p2:
                pt1 = (int(p1.x * width), int(p1.y * height))
                pt2 = (int(p2.x * width), int(p2.y * height))
                cv2.line(frame, pt1, pt2, (255, 255, 255), 2)

        # Draw keypoints
        for i, kp in enumerate(keypoints):
            if kp:
                x, y = int(kp.x * width), int(kp.y * height)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        # Draw angles in a list on the side
        if show_angles and selected_joints:
            margin = 10
            line_height = 20
            x_text = width - 200  # Start 200px from the right
            y_text = margin

            for joint in selected_joints:
                if joint not in JOINT_MAP:
                    continue
                i1, i2, i3 = JOINT_MAP[joint]
                p1, p2, p3 = keypoints[i1], keypoints[i2], keypoints[i3]

                if None in (p1, p2, p3):
                    continue

                angle = calculate_angle(p1, p2, p3)
                label = f"{joint}: {int(angle)}°"

                cv2.putText(frame, label, (x_text, y_text),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                y_text += line_height

        out.write(frame)

    cap.release()
    out.release()

