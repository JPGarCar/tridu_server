from typing import List

from django.core.exceptions import ValidationError
from ninja import Router

from accounts.models import User
from heats.models import Heat
from heats.schema import HeatSchema
from locations.models import Location
from participants.api.comment_api import relay_team_comment_router
from participants.models import RelayTeamComment, RelayParticipant, RelayTeam
from participants.schema.relay_team import (
    RelayTeamCommentSchema,
    RelayTeamCommentCreateSchema,
    RelayTeamParticipantSchema,
    RelayTeamSchema,
    CreateRelayTeamSchema,
    CreateRelayParticipantSchema,
    PatchRelayTeamSchema,
    PatchRelayParticipantSchema,
)
from race.models import RaceType
from race.schema import RaceTypeSchema
from tridu_server.schemas import ErrorObjectSchema

router = Router()

router.add_router("/comments", relay_team_comment_router)


@router.post(
    "/{relay_team_id}/comments",
    tags=["relay team", "comment"],
    response={201: RelayTeamCommentSchema, 409: ErrorObjectSchema},
)
def create_relay_team_comment(
    request, relay_team_id: int, commentSchema: RelayTeamCommentCreateSchema
):
    comment = RelayTeamComment(
        relay_team_id=relay_team_id,
        comment=commentSchema.comment,
        writer=request.user,
    )

    try:
        comment.validate_constraints()
        comment.save()
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error=e, instance_name="Relay Team Comment"
        )

    return 201, comment


@router.get(
    "/{relay_team_id}/comments",
    tags=["relay team", "comment"],
    response={
        200: List[RelayTeamCommentSchema],
    },
)
def get_relay_team_comments(request, relay_team_id: int):
    return 200, RelayTeamComment.objects.filter(relay_team_id=relay_team_id)


@router.patch(
    "/{relay_team_id}/change_race_type",
    tags=["participant"],
    response={201: RelayTeamSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def change_relay_team_race_type(
    request, relay_team_id: int, race_type_schema: RaceTypeSchema
):

    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    if relay_team.heat:
        return (
            409,
            ErrorObjectSchema.for_validation_error(
                instance_name="Relay Team",
                details="Relay Team is in a heat. Please remove them from their heat first.",
            ),
        )

    try:
        new_race_type = RaceType.objects.get(id=race_type_schema.id)
    except RaceType.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Race Type with id {} does not exist".format(race_type_schema.id)
        )

    relay_team.race_type = new_race_type
    relay_team.save()

    return 201, relay_team


@router.patch(
    "/{relay_team_id}/change_heat",
    tags=["participant"],
    response={200: RelayTeamSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def change_relay_team_heat(request, relay_team_id: int, heat_schema: HeatSchema):

    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    if relay_team.heat:
        return (
            409,
            ErrorObjectSchema.for_validation_error(
                instance_name="Relay Team",
                details="Relay Team is in a heat. Please remove them from their heat first.",
            ),
        )

    try:
        new_heat = Heat.objects.get(id=heat_schema.id)
    except Heat.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Heat with id {} does not exist".format(heat_schema.id)
        )

    relay_team.heat = new_heat
    relay_team.save()

    return 201, relay_team


@router.patch(
    "/{relay_team_id}/remove_heat",
    tags=["participant"],
    response={201: RelayTeamSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def remove_relay_team_heat(request, relay_team_id: int):

    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    if not relay_team.heat:
        return (
            409,
            ErrorObjectSchema.for_validation_error(
                instance_name="Relay Team",
                details="Relay Team is not in a heat. Cannot remove from a heat.",
            ),
        )

    relay_team.heat = None
    relay_team.save()

    return 201, relay_team


@router.patch(
    "/{relay_team_id}/deactivate",
    tags=["relay team"],
    response={201: RelayTeamSchema, 404: ErrorObjectSchema},
)
def deactivate_relay_team(request, relay_team_id: int):

    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    relay_team.deactivate()
    relay_team.save()
    return 201, relay_team


@router.patch(
    "/{relay_team_id}/reactivate",
    tags=["relay team"],
    response={201: RelayTeamSchema, 404: ErrorObjectSchema},
)
def reactivate_relay_team(request, relay_team_id: int):

    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    relay_team.activate()
    relay_team.save()
    return 201, relay_team


@router.post(
    "/{relay_team_id}/participants",
    tags=["relay team"],
    response={
        201: RelayTeamParticipantSchema,
        404: ErrorObjectSchema,
        409: ErrorObjectSchema,
    },
)
def add_participant_to_relay_team(
    request, relay_team_id: int, relay_team_member_schema: CreateRelayParticipantSchema
):
    relay_team_member_data = relay_team_member_schema.dict()

    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    try:
        user = User.objects.get(id=relay_team_member_data.get("user"))
    except User.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "User with id {} does not exist".format(relay_team_member_data.get("user"))
        )

    try:
        relay_team_participant = RelayParticipant(
            team=relay_team,
            user=user,
            location=relay_team_member_data.get("location", ""),
        )
        relay_team_participant.validate_constraints()
        relay_team_participant.save()
        return 201, relay_team_participant
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error=e, instance_name="Relay Team Participant"
        )


@router.get(
    "/{relay_team_id}/participants",
    tags=["relay team"],
    response={200: List[RelayTeamParticipantSchema]},
)
def get_relay_team_participants(request, relay_team_id: int):
    return 200, RelayParticipant.objects.filter(team_id=relay_team_id)


@router.patch(
    "/{relay_team_id}/participants/{relay_participant_id}",
    tags=["participant"],
    response={
        201: RelayTeamParticipantSchema,
        409: ErrorObjectSchema,
        404: ErrorObjectSchema,
    },
)
def update_relay_participant(
    request,
    relay_team_id: int,
    relay_participant_id: int,
    relay_participant_schema: PatchRelayParticipantSchema,
):
    try:
        relay_team_participant = RelayParticipant.objects.get(
            id=relay_participant_id, team_id=relay_team_id
        )
    except RelayParticipant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Participant with id {} does not exist".format(relay_participant_id)
        )

    data = relay_participant_schema.dict()

    # update origin of Participant
    if "origin" in data:
        origin_data = data.pop("origin")
        if (
            "country" in origin_data
            and "province" in origin_data
            and "city" in origin_data
        ):
            origin = Location.objects.filter(
                country=origin_data["country"],
                province=origin_data["province"],
                city=origin_data["city"],
            ).first()
            if origin is None:
                origin = Location.objects.create(
                    country=origin_data["country"],
                    province=origin_data["province"],
                    city=origin_data["city"],
                )
            relay_team_participant.origin = origin

    # update participant values
    for key, value in data.items():
        setattr(relay_team_participant, key, value)

    try:
        relay_team_participant.validate_constraints()
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error=e, instance_name="Relay Participant"
        )

    relay_team_participant.save()
    return 201, relay_team_participant


@router.get(
    "/participants/{relay_participant_id}",
    tags=["relay team"],
    response={200: RelayTeamParticipantSchema, 404: ErrorObjectSchema},
)
def get_relay_participant(request, relay_participant_id: int):
    try:
        return 200, RelayParticipant.objects.select_all_related().get(
            id=relay_participant_id
        )
    except RelayParticipant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="Relay Participant with id {} does not exist".format(
                relay_participant_id
            )
        )


@router.patch(
    "/{int:relay_team_id}",
    tags=["relay team"],
    response={200: RelayTeamSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def update_relay_team(
    request, relay_team_id: int, relay_team_schema: PatchRelayTeamSchema
):
    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    data = relay_team_schema.dict()

    # update participant values
    for key, value in data.items():
        setattr(relay_team, key, value)

    try:
        relay_team.validate_constraints()
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error=e, instance_name="Relay Team"
        )

    relay_team.save()
    return 200, relay_team


@router.get(
    "/{str:relay_team_name}",
    tags=["relay team"],
    response={200: RelayTeamSchema, 404: ErrorObjectSchema},
)
def get_relay_team_by_name(request, relay_team_name: str):
    try:
        return 200, RelayTeam.objects.get(name=relay_team_name)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with name {} does not exist.".format(relay_team_name)
        )


@router.post(
    "/", tags=["relay name"], response={201: RelayTeamSchema, 409: ErrorObjectSchema}
)
def create_relay_team(request, create_relay_team_schema: CreateRelayTeamSchema):

    relay_team_data = create_relay_team_schema.dict()

    try:
        relay_team = RelayTeam(
            name=relay_team_data.get("name"),
            bib_number=relay_team_data.get("bib_number"),
            race_id=relay_team_data.get("race"),
            race_type_id=relay_team_data.get("race_type"),
        )

        relay_team.validate_constraints()
        relay_team.save()

        return 201, relay_team
    except ValidationError as validation_error:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error, "Relay Team"
        )
