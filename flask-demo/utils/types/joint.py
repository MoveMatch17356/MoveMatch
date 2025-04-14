from enum import Enum

class Joint(str, Enum):
    RIGHT_ELBOW = "right_elbow"
    LEFT_ELBOW = "left_elbow"
    RIGHT_KNEE = "right_knee"
    LEFT_KNEE = "left_knee"
    RIGHT_SHOULDER = "right_shoulder"
    LEFT_SHOULDER = "left_shoulder"
    RIGHT_HIP = "right_hip"
    LEFT_HIP = "left_hip"
