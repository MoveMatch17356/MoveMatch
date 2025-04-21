from utils.types.joint import Joint

class Movement:
    def __init__(self, key: str, label: str, joints: list[Joint]):
        self.key = key
        self.label = label
        self.joints = joints

    def __repr__(self):
        return f"<Movement: {self.label} ({self.key})>"
