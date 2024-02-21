from ninja import ModelSchema, Schema

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
    class Meta:
        model = RaceType
        fields = ("id", "name", "participants_allowed", "ftt_allowed")


class RaceTypeBibInfoSchema(RaceTypeSchema):
    smallest_bib: int
    largest_bib: int
    count: int


class CreateRaceTypeSchema(ModelSchema):
    class Meta:
        model = RaceType
        fields = ("name", "participants_allowed", "ftt_allowed")


class RaceTypeStatSchema(Schema):
    race_type: RaceTypeSchema
    registered: int
    allowed: int
    ftt_registered: int
    ftt_allowed: int
