from utils.types.joint import Joint
from utils.types.movement import Movement

class Sport:
    def __init__(self, key: str, label: str, movements: list[Movement]):
        self.key = key
        self.label = label
        self.movements = movements

    def __repr__(self) -> str:
        return f"<Sport: {self.label} ({self.key})>"

# Example sports (can be moved into a config if needed)
TENNIS = Sport(
    key="tennis",
    label="Tennis",
    movements=[
        Movement("tennis_serve", "Serve", [Joint.RIGHT_SHOULDER, Joint.RIGHT_ELBOW]),
        Movement("tennis_forehand", "Forehand", [Joint.RIGHT_SHOULDER]),
    ],
)

ALL_SPORTS = {TENNIS.key: TENNIS}
ALL_MOVEMENTS = {m.key: m for s in ALL_SPORTS.values() for m in s.movements}
