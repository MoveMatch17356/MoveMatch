import cv2
import mediapipe as mp
from video_analysis.types import Frame, Pose, Point3D

def extract_3d_poses(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)
    mp_pose = mp.solutions.pose

    with mp_pose.Pose(static_image_mode=False, model_complexity=2) as pose:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            keypoints = [Point3D(lm.x, lm.y, lm.z) if result.pose_landmarks else None for lm in result.pose_landmarks.landmark] if result.pose_landmarks else [None] * 33

            frames.append(Frame(time=time_sec, pose=Pose(keypoints=keypoints)))

    cap.release()
    return frames
