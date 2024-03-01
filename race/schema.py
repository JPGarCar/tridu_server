from typing import List

from ninja import ModelSchema, Schema

from checkins.schema import CheckInSchema
from race.models import Race, RaceType


class RaceSchema(ModelSchema):
    class Meta:
        model = Race
        fields = ("id", "name", "date_created")


class CreateRaceSchema(ModelSchema):
    class Meta:
        model = Race
        fields = ("name",)


class RaceTypeSchema(ModelSchema):
    checkins: List[CheckInSchema] = None

    class Meta:
        model = RaceType
        fields = (
            "id",
            "name",
            "participants_allowed",
            "ftt_allowed",
            "needs_swim_time",
        )


class CheckinLessRaceTypeSchema(ModelSchema):

    class Meta:
        model = RaceType
        fields = (
            "id",
            "name",
            "participants_allowed",
            "ftt_allowed",
            "needs_swim_time",
        )


class RaceTypeBibInfoSchema(ModelSchema):
    smallest_bib: int
    largest_bib: int
    count: int

    class Meta:
        model = RaceType
        fields = (
            "id",
            "name",
            "participants_allowed",
            "ftt_allowed",
        )


class CreateRaceTypeSchema(ModelSchema):
    checkins: List[CheckInSchema] = None

    class Meta:
        model = RaceType
        fields = ("name", "participants_allowed", "ftt_allowed", "needs_swim_time")


class PatchRaceTypeSchema(ModelSchema):
    checkins: List[CheckInSchema] = None

    class Meta:
        model = RaceType
        fields = ("name", "participants_allowed", "ftt_allowed", "needs_swim_time")
        fields_optional = "__all__"


class RaceTypeStatSchema(Schema):
    race_type: RaceTypeSchema
    registered: int
    allowed: int
    ftt_registered: int
    ftt_allowed: int
