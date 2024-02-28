from typing import List

from django.db.models import Min, Max, Count
from ninja import Router
from ninja.pagination import paginate

from heats.heat_service import (
    check_auto_schedule_is_ready,
    auto_schedule_heats,
    AutoSchedulerException,
)
from heats.models import Heat
from heats.schema import HeatSchema
from participants.models import Participant, RelayParticipant, RelayTeam
from participants.schema.particiapnt import ParticipantSchema, ParticipationSchema
from race.models import RaceType, Race
from race.schema import (
    RaceSchema,
    CreateRaceSchema,
    RaceTypeStatSchema,
    RaceTypeBibInfoSchema,
)
from tridu_server.schemas import ErrorObjectSchema

router = Router()


@router.get("/", tags=["races"], response={200: List[RaceSchema]})
def get_races(request):
    return 200, Race.objects.filter(is_active=True).all()


@router.post("/", tags=["races"], response={200: RaceSchema, 409: RaceSchema})
def create_race(request, race_schema: CreateRaceSchema):
    race, isNew = Race.objects.get_or_create(**race_schema.dict())
    if isNew:
        return 201, race
    else:
        return 200, race


@router.get(
    "/{race_id}/heats", tags=["heats", "races"], response={200: List[HeatSchema]}
)
def get_race_heats(request, race_id: int, race_type_id: int = None):
    heats = Heat.objects.filter(race_id=race_id).select_related("race", "race_type")

    if race_type_id:
        heats = heats.for_race_type(race_type_id)

    return 200, heats


@router.get(
    "/{race_id}/heats/auto_schedule/ready",
    tags=["heats", "races"],
    response={200: List[str]},
)
def get_race_ready_for_auto_schedule_heats(request, race_id: int):
    """Returns empty list if ready, else a list of errors."""
    return 200, check_auto_schedule_is_ready(race_id=race_id)


@router.post(
    "/{race_id}/heats/auto_schedule",
    tags=["heats", "races"],
    response={200: bool, 400: ErrorObjectSchema},
)
def auto_schedule_race_heats(request, race_id: int):
    try:
        auto_schedule_heats(race_id=race_id)
        return 200, True
    except AutoSchedulerException as e:
        return 400, ErrorObjectSchema(
            title="Automatic Scheduler Error", status=400, details=e.__str__()
        )


@router.get(
    "/{race_id}/participants/invalid_swim_time/",
    tags=["participant"],
    response={200: List[ParticipantSchema]},
)
def get_race_participants_with_invalid_swim_time(request, race_id: int):
    """Returns all the active participants of the given race that have an invalid swim time."""
    race_type_ids_without_swim_time = (
        RaceType.objects.does_not_need_swim_time().values_list("id", flat=True)
    )

    return (
        200,
        Participant.objects.active()
        .for_race_id(race_id)
        .not_in_race_types(race_type_ids_without_swim_time)
        .with_invalid_swim_time(),
    )


@router.get(
    "/{race_id}/participants",
    tags=["participant", "races"],
    response={200: List[ParticipantSchema]},
)
@paginate
def get_race_participants(request, race_id: int, bib_number: int = None):
    participants = Participant.objects.for_race_id(race_id=race_id)

    if bib_number is not None:
        participants = participants.filter(bib_number__regex=r"{}".format(bib_number))

    return participants


@router.get(
    "/{race_id}/participations",
    tags=["participant", "races"],
    response={200: List[ParticipationSchema]},
)
def get_race_participations(
    request, race_id: int, bib_number: int = None, limit: int = 100, offset: int = 0
):
    """
    Returns all the normal and Relay Participants for this race.
    """

    participants = Participant.objects.for_race_id(race_id=race_id)
    relay_participants = RelayParticipant.objects.filter(team__race_id=race_id)

    if bib_number is not None:
        participants = participants.filter(bib_number__regex=r"{}".format(bib_number))
        relay_participants = relay_participants.filter(
            team__bib_number__regex=r"{}".format(bib_number)
        )

    participations = []

    for participant in participants[offset : offset + limit]:
        participations.append(
            ParticipationSchema(
                id=participant.id,
                race=participant.race,
                type=ParticipationSchema.ParticipationTypes.PARTICIPANT,
                user=participant.user,
                bib_number=participant.bib_number,
            )
        )

    for relay_participant in relay_participants[offset : offset + limit]:
        participations.append(
            ParticipationSchema(
                id=relay_participant.id,
                race=relay_participant.team.race,
                type=ParticipationSchema.ParticipationTypes.RELAY_PARTICIPANT,
                user=relay_participant.user,
                bib_number=relay_participant.team.bib_number,
            )
        )

    return 200, participations


@router.get(
    "/{race_id}/stats", tags=["races"], response={200: List[RaceTypeStatSchema]}
)
def get_race_stats(request, race_id: int):

    race_types_query = RaceType.objects.for_race(race_id).distinct()

    race_type_counts = {
        race_type.id: {"ftt_registered": 0, "registered": 0}
        for race_type in race_types_query
    }

    # participants
    for (
        race_type_count
    ) in Participant.objects.active_for_race_grouped_by_race_type_and_ftt_count(
        race_id
    ):
        race_type_id = race_type_count.get("race_type")
        is_ftt = race_type_count.get("is_ftt")
        if is_ftt:
            race_type_counts[race_type_id]["ftt_registered"] = race_type_count.get(
                "count"
            )
        else:
            race_type_counts[race_type_id]["registered"] = race_type_count.get("count")

    # relay teams
    for race_type_count in RelayTeam.objects.active_for_race_grouped_by_race_type_count(
        race_id
    ):
        race_type_id = race_type_count.get("race_type")
        race_type_counts[race_type_id]["registered"] = race_type_count.get("count")

    race_type_stats = []

    for race_type in race_types_query:
        race_type_count = race_type_counts.get(race_type.id, None)
        race_type_stats.append(
            RaceTypeStatSchema(
                race_type=race_type,
                registered=race_type_count.get("registered") if race_type_count else 0,
                ftt_registered=(
                    race_type_count.get("ftt_registered") if race_type_count else 0
                ),
                allowed=race_type.participants_allowed,
                ftt_allowed=race_type.ftt_allowed,
            )
        )

    return 200, race_type_stats


@router.get(
    "/{race_id}/participants/disabled",
    tags=["participant", "races"],
    response={200: List[ParticipantSchema]},
)
def get_race_participants_disabled(request, race_id: int):
    return 200, Participant.objects.inactive().for_race_id(race_id)


@router.get(
    "/{race_id}/racetypes/bib_info",
    tags=["race type"],
    response={200: List[RaceTypeBibInfoSchema]},
)
def get_race_bib_info_per_race_type(request, race_id: int):

    bib_info_schema_items: List[RaceTypeBibInfoSchema] = []

    for race_type in RaceType.objects.for_race(race_id).annotate(
        p_smallest_bib=Min("participants__bib_number"),
        p_largest_bib=Max("participants__bib_number"),
        p_count=Count("participants__bib_number"),
        r_smallest_bib=Min("relay_teams__bib_number"),
        r_largest_bib=Max("relay_teams__bib_number"),
        r_count=Count("relay_teams__bib_number"),
    ):
        bib_info_schema_items.append(
            RaceTypeBibInfoSchema(
                **race_type.__dict__,
                smallest_bib=(
                    race_type.p_smallest_bib or 0
                    if race_type.r_smallest_bib is None
                    else (
                        race_type.r_smallest_bib or 0
                        if race_type.p_smallest_bib is None
                        else min(race_type.p_smallest_bib, race_type.r_smallest_bib)
                    )
                ),
                largest_bib=(
                    race_type.p_largest_bib or 0
                    if race_type.r_largest_bib is None
                    else (
                        race_type.r_largest_bib or 0
                        if race_type.p_largest_bib is None
                        else max(race_type.p_largest_bib, race_type.r_largest_bib)
                    )
                ),
                count=race_type.p_count or 0 + race_type.r_count or 0,
            )
        )

    return 200, bib_info_schema_items


@router.delete(
    "/{race_id}", tags=["races"], response={204: None, 404: ErrorObjectSchema}
)
def delete_race(request, race_id: int):
    try:
        Race.objects.get(id=race_id).delete()
        return 204
    except Race.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="Race with id {} does not exist".format(race_id)
        )


@router.get(
    "/{race_id}", tags=["races"], response={200: RaceSchema, 404: ErrorObjectSchema}
)
def get_race(request, race_id: int):
    try:
        return 200, Race.objects.get(id=race_id)
    except Race.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="Race with id {} does not exist".format(race_id)
        )
