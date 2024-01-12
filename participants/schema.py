from ninja import Field, ModelSchema

from heats.schema import HeatSchema
from locations.schema import LocationSchema
from participants.models import Participant, ParticipantComment
from race.schema import RaceSchema, RaceTypeSchema


class ParticipantSchema(ModelSchema):
    origin: LocationSchema
    race: RaceSchema
    race_type: RaceTypeSchema
    heat: HeatSchema

    class Meta:
        model = Participant
        fields = (
            "id",
            "bib_number",
            "is_ftt",
            "team",
            "swim_time",
        )


class ParticipantCommentSchema(ModelSchema):
    writer_name: str = Field(None, alias="writer.first_name")

    class Meta:
        model = ParticipantComment
        fields = ("id", "participant", "comment", "creation_date")
