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
    # Add more as needed

    @classmethod
    def list(cls):
        return list(map(lambda j: j.value, cls))

class Sport(str, Enum):
    TENNIS_SERVE = "tennis_serve"
    SQUAT = "squat"
    JUMP = "jump"
    PITCH = "pitch"

    def label(self):
        return {
            Sport.TENNIS_SERVE: "Tennis Serve",
            Sport.SQUAT: "Squat",
            Sport.JUMP: "Vertical Jump",
            Sport.PITCH: "Baseball Pitch",
        }[self]

    @classmethod
    def list(cls):
        return list(cls)

    @classmethod
    def choices(cls):
        return [(sport.value, sport.label()) for sport in cls]