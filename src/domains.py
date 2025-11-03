from dataclasses import dataclass


@dataclass
class NotificationDTO:
    team_1: str
    team_2: str
    status: str
