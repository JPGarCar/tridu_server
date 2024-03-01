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
        return obj.participants.active().aggregate(Avg("swim_time"))[
            "swim_time__avg"
        ] or datetime.timedelta(0)

    @staticmethod
    def resolve_participant_count(obj: Heat) -> int:
        return obj.participants.active().count()

    @staticmethod
    def resolve_name(obj: Heat) -> str:
        return obj.__str__()

    class Meta:
        model = Heat
        fields = (
            "id",
            "termination",
            "start_datetime",
            "color",
            "ideal_capacity",
            "pool",
        )
        fields_optional = ("pool",)


class PatchHeatSchema(ModelSchema):
    class Meta:
        model = Heat
        fields = ("termination", "start_datetime", "color", "ideal_capacity", "pool")
        fields_optional = "__all__"


class CreateHeatSchema(ModelSchema):
    class Meta:
        model = Heat
        fields = (
            "id",
            "termination",
            "start_datetime",
            "color",
            "ideal_capacity",
            "pool",
            "race",
            "race_type",
        )
        fields_optional = ("color", "ideal_capacity", "pool")
