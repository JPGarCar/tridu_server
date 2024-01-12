from ninja import ModelSchema

from heats.models import Heat
from race.schema import RaceTypeSchema, RaceSchema


class HeatSchema(ModelSchema):
    race_type: RaceTypeSchema
    race: RaceSchema

    class Meta:
        model = Heat
        fields = ("id", "termination", "start_datetime", "color")
