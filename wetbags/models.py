from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from django.utils import timezone


@dataclass
class Wetbag:
    """A class to keep track of Participant Wetbags during the race."""

    class WetbagStatus(Enum):
        """Possible states of a wetbag."""

        NEVER_RECEIVED = "Never Received"
        RECEIVED = "Received"
        REQUESTED = "Requested"
        PICKED_UP = "Picked Up"

    participant_id: int
    race_id: int
    bib_number: int
    heat_id: int
    color: str
    changed_datetime: datetime
    requested_datetime: datetime = timezone.now()
    status: WetbagStatus = WetbagStatus.NEVER_RECEIVED

    @staticmethod
    def create_id(
        race_id: int, participant_id: int, bib_number: int, heat_id: int
    ) -> str:
        return str(race_id) + str(heat_id) + str(participant_id) + str(bib_number)

    @property
    def id(self) -> str:
        return Wetbag.create_id(
            self.race_id, self.participant_id, self.bib_number, self.heat_id
        )

    @staticmethod
    def from_dict(source: dict) -> "Wetbag":
        wetbag = Wetbag(**source)
        wetbag.status = Wetbag.WetbagStatus(wetbag.status)
        return wetbag

    @staticmethod
    def changed_to_dict(wetbag_data: dict[str, any]) -> dict:
        if "status" in wetbag_data.keys():
            wetbag_data["status"] = wetbag_data["status"].value

        return wetbag_data

    def to_dict(self) -> dict:
        return {
            "race_id": self.race_id,
            "participant_id": self.participant_id,
            "bib_number": self.bib_number,
            "requested_datetime": self.requested_datetime,
            "changed_datetime": self.changed_datetime,
            "status": self.status.value,
            "heat_id": self.heat_id,
            "color": self.color,
        }
