from ninja import ModelSchema

from race.models import Race, RaceType


class RaceSchema(ModelSchema):
    class Meta:
        model = Race
        fields = ("id", "name", "date_created")


class RaceTypeSchema(ModelSchema):
    class Meta:
        model = RaceType
        fields = ("id", "name")


class CreateRaceTypeSchema(ModelSchema):
    class Meta:
        model = RaceType
        fields = ("name",)
