import numpy as np
from video_analysis.types import Point3D

JOINT_MAP = {
    'left_elbow': [11, 13, 15],
    'right_elbow': [12, 14, 16],
    'left_knee': [23, 25, 27],
    'right_knee': [24, 26, 28],
    'left_hip': [11, 23, 25],
    'right_hip': [12, 24, 26],
    'left_shoulder': [13, 11, 23],
    'right_shoulder': [14, 12, 24],
}

def calculate_angle(a, b, c):
    a_vec = np.array([a.x - b.x, a.y - b.y, a.z - b.z])
    c_vec = np.array([c.x - b.x, c.y - b.y, c.z - b.z])
    dot = np.dot(a_vec, c_vec)
    norm = np.linalg.norm(a_vec) * np.linalg.norm(c_vec)
    return float('nan') if norm == 0 else np.degrees(np.arccos(np.clip(dot / norm, -1.0, 1.0)))

def compute_joint_angles(frames, joints):
    angles = {joint: [] for joint in joints}
    for frame in frames:
        keypoints = frame.pose.keypoints
        for joint in joints:
            if joint in JOINT_MAP:
                i1, i2, i3 = JOINT_MAP[joint]
                pts = [keypoints[i] for i in (i1, i2, i3)]
                angle = calculate_angle(*pts) if all(pts) else None
                angles[joint].append(angle)
            else:
                angles[joint].append(None)
    return angles
