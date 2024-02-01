import datetime

from django.db.models import Avg
from ninja import ModelSchema

from heats.models import Heat
from race.schema import RaceTypeSchema, RaceSchema


class HeatSchema(ModelSchema):
    race_type: RaceTypeSchema
    race: RaceSchema
    name: str
    participant_count: int
    avg_swim_time: datetime.timedelta

    @staticmethod
    def resolve_avg_swim_time(obj: Heat) -> datetime.timedelta:
        return obj.participants.aggregate(Avg("swim_time"))["swim_time__avg"]

    @staticmethod
    def resolve_participant_count(obj: Heat) -> int:
        return obj.participants.count()

    @staticmethod
    def resolve_name(obj: Heat) -> str:
        return obj.__str__()

    class Meta:
        model = Heat
        fields = ("id", "termination", "start_datetime", "color", "ideal_capacity")


class PatchHeatSchema(ModelSchema):
    class Meta:
        model = Heat
        fields = ("termination", "start_datetime", "color", "ideal_capacity")


class CreateHeatSchema(ModelSchema):
    class Meta:
        model = Heat
        fields = (
            "id",
            "termination",
            "start_datetime",
            "color",
            "ideal_capacity",
            "race",
            "race_type",
        )
        fields_optional = ("color", "ideal_capacity")
