from ninja import Field, ModelSchema

from accounts.schema import UserSchema
from heats.schema import HeatSchema
from locations.schema import LocationSchema
from participants.models import Participant, ParticipantComment
from race.schema import RaceSchema, RaceTypeSchema


class ParticipantSchema(ModelSchema):
    origin: LocationSchema | None = None
    race: RaceSchema
    race_type: RaceTypeSchema
    heat: HeatSchema | None = None
    user: UserSchema

    class Meta:
        model = Participant
        fields = (
            "id",
            "bib_number",
            "is_ftt",
            "team",
            "swim_time",
            "date_changed",
            "is_active",
        )
        fields_optional = (
            "team",
            "swim_time",
        )


class CreateParticipantSchema(ModelSchema):
    origin: LocationSchema

    class Meta:
        model = Participant
        fields = ("bib_number", "is_ftt", "team", "swim_time", "race", "race_type")


class CreateParticipantBulkSchema(ModelSchema):
    city: str | None = None
    country: str | None = None
    province: str | None = None

    class Meta:
        model = Participant
        fields = (
            "bib_number",
            "is_ftt",
            "team",
            "swim_time",
            "race",
            "race_type",
            "user",
        )
        fields_optional = (
            "team",
            "swim_time",
        )


class PatchParticipantSchema(ModelSchema):
    origin: LocationSchema

    class Meta:
        model = Participant
        fields = ("id", "bib_number", "is_ftt", "team", "swim_time")
        fields_optional = "__all__"


class ParticipantCommentSchema(ModelSchema):
    writer_name: str = Field(None, alias="writer.first_name")

    class Meta:
        model = ParticipantComment
        fields = ("id", "participant", "comment", "creation_date")


class ParticipantCommentCreateSchema(ModelSchema):
    class Meta:
        model = ParticipantComment
        fields = ("comment",)
