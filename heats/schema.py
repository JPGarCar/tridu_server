from ninja import ModelSchema

from heats.models import Heat
from race.schema import RaceTypeSchema, RaceSchema


class HeatSchema(ModelSchema):
    race_type: RaceTypeSchema
    race: RaceSchema
    name: str

    @staticmethod
    def resolve_name(obj: Heat) -> str:
        return obj.__str__()

    class Meta:
        model = Heat
        fields = ("id", "termination", "start_datetime", "color")
