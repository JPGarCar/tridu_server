from ninja import ModelSchema, Field

from accounts.schema import UserSchema
from heats.schema import HeatSchema
from locations.schema import LocationSchema
from race.schema import RaceTypeSchema, RaceSchema

from participants.models import RelayTeam, RelayParticipant, RelayTeamComment


class RelayTeamSchema(ModelSchema):
    race: RaceSchema
    race_type: RaceTypeSchema
    heat: HeatSchema | None = None

    class Meta:
        model = RelayTeam
        fields = ("id", "is_active", "bib_number", "name")


class CreateRelayTeamSchema(ModelSchema):

    class Meta:
        model = RelayTeam
        fields = ("bib_number", "name", "race", "race_type")


class PatchRelayTeamSchema(ModelSchema):

    class Meta:
        model = RelayTeam
        fields = (
            "bib_number",
            "name",
        )
        fields_optional = (
            "name",
            "bib_number",
        )


class CreateRelayParticipantSchema(ModelSchema):
    class Meta:
        model = RelayParticipant
        fields = ("location", "user", "team")
        fields_optional = ("location",)


class PatchRelayParticipantSchema(ModelSchema):
    origin: LocationSchema | None = None

    class Meta:
        model = RelayParticipant
        fields = ("location",)
        fields_optional = "__all__"


class RelayTeamParticipantSchema(ModelSchema):
    origin: LocationSchema | None = None
    user: UserSchema
    team: RelayTeamSchema

    class Meta:
        model = RelayParticipant
        fields = ("id", "date_changed", "is_active", "location")
        fields_optional = ("location",)


class RelayTeamCommentSchema(ModelSchema):
    writer_name: str = Field(None, alias="writer.first_name")

    class Meta:
        model = RelayTeamComment
        fields = ("id", "relay_team", "comment", "creation_date")


class RelayTeamCommentCreateSchema(ModelSchema):
    class Meta:
        model = RelayTeamComment
        fields = ("comment",)
