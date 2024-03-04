import datetime
from enum import Enum
from typing import List

from ninja import Field, ModelSchema, Schema

from accounts.schema import UserSchema, DownloadUserSchema
from checkins.schema import CheckInUserBaseSchema
from heats.schema import HeatSchema, DownloadHeatSchema
from locations.schema import LocationSchema, DownloadLocationSchema
from participants.models import (
    Participant,
    ParticipantComment,
)
from race.schema import (
    RaceSchema,
    RaceTypeSchema,
    DownloadRaceTypeSchema,
)


class ParticipationSchema(Schema):
    """
    A simple Participation schema that allows returning IDs for Participant and RelayParticipant Models.
    """

    class ParticipationTypes(Enum):
        PARTICIPANT = "participant"
        RELAY_PARTICIPANT = "relay_participant"

    class Config(Schema.Config):
        use_enum_values = True

    id: int
    race: RaceSchema
    type: ParticipationTypes
    user: UserSchema
    bib_number: int
    swim_time: datetime.timedelta | None = None


class ParticipantSchema(ModelSchema):
    origin: LocationSchema | None = None
    race: RaceSchema
    race_type: RaceTypeSchema
    heat: HeatSchema | None = None
    user: UserSchema
    checkins: List[CheckInUserBaseSchema] = []

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
            "location",
            "waiver_signed",
        )
        fields_optional = ("team", "swim_time", "location")


class DownloadInfoParticipantSchema(ModelSchema):
    origin: DownloadLocationSchema | None = None
    race_type: DownloadRaceTypeSchema
    user: DownloadUserSchema
    heat: DownloadHeatSchema | None = None
    swim_time: str | None = None

    @staticmethod
    def resolve_swim_time(obj: Participant) -> str:
        return str(obj.swim_time)

    class Meta:
        model = Participant
        fields = (
            "bib_number",
            "team",
            "location",
        )
        fields_optional = ("team", "location")


class CreateParticipantSchema(ModelSchema):
    origin: LocationSchema | None = None

    class Meta:
        model = Participant
        fields = (
            "bib_number",
            "is_ftt",
            "team",
            "swim_time",
            "race",
            "race_type",
            "location",
            "waiver_signed",
        )
        fields_optional = (
            "swim_time",
            "team",
            "location",
        )


class CreateParticipantBulkSchema(ModelSchema):
    city: str | None = None
    country: str | None = None
    province: str | None = None
    swim_time: str | None = None

    class Meta:
        model = Participant
        fields = (
            "bib_number",
            "is_ftt",
            "team",
            "race",
            "race_type",
            "user",
            "location",
        )
        fields_optional = ("team", "location")


class PatchParticipantSchema(ModelSchema):
    origin: LocationSchema | None = None

    class Meta:
        model = Participant
        fields = (
            "bib_number",
            "is_ftt",
            "team",
            "swim_time",
            "location",
            "waiver_signed",
        )
        fields_optional = "__all__"


class MassPatchParticipantSchema(ModelSchema):

    class Meta:
        model = Participant
        fields = (
            "is_ftt",
            "waiver_signed",
        )
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
