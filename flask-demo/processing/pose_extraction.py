import cv2
import mediapipe as mp
import os
import json
from typing import List
from utils.types import Point3D, Pose, Frame

mp_pose = mp.solutions.pose

def extract_3d_poses(video_path: str, cache_path: str) -> List[Frame]:
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            raw = json.load(f)
        return _deserialize_frames(raw)

    frames: List[Frame] = []
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    with mp_pose.Pose(static_image_mode=False, model_complexity=2) as pose:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            time_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            if result.pose_landmarks:
                keypoints = [
                    Point3D(lm.x, lm.y, lm.z) for lm in result.pose_landmarks.landmark
                ]
            else:
                keypoints = [None] * 33  # MediaPipe always has 33 keypoints

            frames.append(Frame(time=time_sec, pose=Pose(keypoints=keypoints)))

    cap.release()

    # Cache it
    with open(cache_path, 'w') as f:
        json.dump(_serialize_frames(frames), f)

    return frames

# JSON-safe serialization
def _serialize_frames(frames: List[Frame]):
    return [
        {
            "time": frame.time,
            "pose": [
                {"x": p.x, "y": p.y, "z": p.z} if p else None
                for p in frame.pose.keypoints
            ],
        }
        for frame in frames
    ]

def _deserialize_frames(data: List[dict]) -> List[Frame]:
    return [
        Frame(
            time=frame["time"],
            pose=Pose(keypoints=[
                Point3D(**kp) if kp else None for kp in frame["pose"]
            ])
        )
        for frame in data
    ]
