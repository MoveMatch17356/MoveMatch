# utils/types.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

@dataclass
class Point3D:
    x: float
    y: float
    z: float

@dataclass
class Pose:
    keypoints: List[Optional[Point3D]]  # None if undetected

@dataclass
class Frame:
    time: float  # seconds
    pose: Pose

class Joint(str, Enum):
    RIGHT_ELBOW = "right_elbow"
    LEFT_ELBOW = "left_elbow"
    RIGHT_KNEE = "right_knee"
    LEFT_KNEE = "left_knee"
    RIGHT_SHOULDER = "right_shoulder"
    LEFT_SHOULDER = "left_shoulder"
    RIGHT_HIP = "right_hip"
    LEFT_HIP = "left_hip"
    RIGHT_ANKLE = "right_ankle"
    LEFT_ANKLE = "left_ankle"
    RIGHT_WRIST = "right_wrist"
    LEFT_WRIST = "left_wrist"

    @classmethod
    def list(cls):
        return list(map(lambda j: j.value, cls))

    @property
    def landmark_indices(self) -> Optional[List[int]]:
        return {
            Joint.RIGHT_ELBOW: [12, 14, 16],
            Joint.LEFT_ELBOW: [11, 13, 15],
            Joint.RIGHT_KNEE: [24, 26, 28],
            Joint.LEFT_KNEE: [23, 25, 27],
            Joint.RIGHT_SHOULDER: [14, 12, 24],
            Joint.LEFT_SHOULDER: [13, 11, 23],
            Joint.RIGHT_HIP: [12, 24, 26],
            Joint.LEFT_HIP: [11, 23, 25],
            Joint.RIGHT_ANKLE: [26, 28, 32],
            Joint.LEFT_ANKLE: [25, 27, 31],
            Joint.RIGHT_WRIST: [14, 16, 22],
            Joint.LEFT_WRIST: [13, 15, 21],
        }.get(self, None)
