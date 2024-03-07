from datetime import datetime

from ninja import Schema

from wetbags.models import Wetbag


class WetbagSchema(Schema):
    participant_id: int
    race_id: int
    bib_number: int
    heat_id: int
    color: str
    requested_datetime: datetime
    changed_datetime: datetime
    status: Wetbag.WetbagStatus
    id: str

    @staticmethod
    def resolve_id(obj: Wetbag) -> str:
        return obj.id

    class Config(Schema.Config):
        use_enum_values = True


class CreateWetbagSchema(Schema):
    participant_id: int
    race_id: int
    bib_number: int
    heat_id: int
    status: Wetbag.WetbagStatus = Wetbag.WetbagStatus.NEVER_RECEIVED


class UpdateWetbagSchema(Schema):
    status: Wetbag.WetbagStatus | None = None
    heat_id: int | None = None
