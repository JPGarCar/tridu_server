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
        fields = ("id", "name")


class CreateRaceTypeSchema(ModelSchema):
    class Meta:
        model = RaceType
        fields = ("name",)


class RaceTypeStatSchema(Schema):
    race_type: RaceTypeSchema
    registered: int
    allowed: int
    ftt_registered: int
    ftt_allowed: int
