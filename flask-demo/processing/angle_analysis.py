import numpy as np
from typing import List, Dict, Tuple, Optional
from utils.types import Point3D, Pose, Frame

# Joint map: keypoint indices from MediaPipe
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

def calculate_angle(a: Point3D, b: Point3D, c: Point3D) -> float:
    a_vec = np.array([a.x - b.x, a.y - b.y, a.z - b.z])
    c_vec = np.array([c.x - b.x, c.y - b.y, c.z - b.z])

    dot_product = np.dot(a_vec, c_vec)
    norm_product = np.linalg.norm(a_vec) * np.linalg.norm(c_vec)

    if norm_product == 0:
        return float('nan')

    angle_rad = np.arccos(np.clip(dot_product / norm_product, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def compute_joint_angles(frames: List[Frame], joints: List[str]) -> Dict[str, List[Optional[float]]]:
    joint_angles: Dict[str, List[Optional[float]]] = {joint: [] for joint in joints}

    for frame in frames:
        keypoints = frame.pose.keypoints
        for joint in joints:
            if joint not in JOINT_MAP:
                joint_angles[joint].append(None)
                continue

            i1, i2, i3 = JOINT_MAP[joint]
            p1, p2, p3 = keypoints[i1], keypoints[i2], keypoints[i3]

            if None in (p1, p2, p3):
                joint_angles[joint].append(None)
            else:
                angle = calculate_angle(p1, p2, p3)
                joint_angles[joint].append(angle)

    return joint_angles
