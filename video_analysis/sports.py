# utils/sports.py
from dataclasses import dataclass
from typing import List, Dict
from video_analysis.types import Joint

@dataclass
class Technique:
    key: str
    label: str
    joints: List[Joint]
    # videos: List[str]

@dataclass
class Sport:
    key: str
    label: str
    techniques: List[Technique]

# Example data
TENNIS = Sport(
    key="tennis",
    label="Tennis",
    techniques=[
        Technique("serve", "Serve", [Joint.RIGHT_SHOULDER, Joint.RIGHT_ELBOW, Joint.RIGHT_SHOULDER]),
        Technique("forehand", "Forehand", [Joint.RIGHT_KNEE, Joint.LEFT_KNEE, Joint.RIGHT_ELBOW]),
    ],
)

SOCCER = Sport(
    key="soccer",
    label="Soccer",
    techniques=[
        Technique("pass", "Pass", [Joint.RIGHT_KNEE, Joint.RIGHT_HIP]),
        Technique("kick", "Kick", [Joint.RIGHT_KNEE, Joint.RIGHT_HIP, Joint.RIGHT_ANKLE]),
    ],
)

RUNNING = Sport(
    key="running",
    label="Running",
    techniques=[
        Technique("sprint", "Sprint", [Joint.RIGHT_KNEE, Joint.RIGHT_HIP]),
    ],
)

ALL_SPORTS: Dict[str, Sport] = {
    TENNIS.key: TENNIS,
    SOCCER.key: SOCCER,
    RUNNING.key: RUNNING,
}
