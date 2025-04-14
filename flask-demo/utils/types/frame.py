# utils/types/frame.py
from dataclasses import dataclass
from typing import List, Optional

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
