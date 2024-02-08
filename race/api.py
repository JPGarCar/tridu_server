from typing import List

from ninja import Router

from participants.models import Participant
from participants.schema import ParticipantSchema
from race.models import RaceType, Race
from race.schema import RaceTypeSchema, RaceSchema, CreateRaceSchema, RaceTypeStatSchema

router = Router()


@router.get("/racetypes", tags=["racetypes"], response={200: List[RaceTypeSchema]})
def get_race_types(request):
    return 200, RaceType.objects.filter(is_active=True).all()


@router.post(
    "/racetypes",
    tags=["racetypes"],
    response={201: RaceTypeSchema, 409: RaceTypeSchema},
)
def create_race_type(request, race_type_schema: RaceTypeSchema):
    race_type, created = RaceType.objects.get_or_create(**race_type_schema.dict())
    if created:
        return 201, race_type
    else:
        return 409, race_type


@router.delete("/racetypes/{id}", tags=["racetypes"], response={204: None, 404: str})
def delete_race(request, id: int):
    try:
        race = RaceType.objects.get(id=id)
        race.delete()
        return 204
    except RaceType.DoesNotExist:
        return 404, "Race Type not found."


@router.get("/", tags=["races"], response={200: List[RaceSchema]})
def get_races(request):
    return 200, Race.objects.filter(is_active=True).all()


@router.post("/", tags=["races"], response={201: RaceSchema})
def create_race(request, race_schema: CreateRaceSchema):
    race, isNew = Race.objects.get_or_create(**race_schema.dict())
    return 201, race


@router.get(
    "/{race_id}/stats", tags=["races"], response={200: List[RaceTypeStatSchema]}
)
def get_race_stats(request, race_id: int):

    race_types_query = RaceType.objects.filter(participants__race_id=race_id).distinct()

    race_type_counts = {
        race_type.id: {"ftt_registered": 0, "registered": 0}
        for race_type in race_types_query
    }

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
    tags=["participants", "races"],
    response={200: List[ParticipantSchema]},
)
def race_participants_disabled(request, race_id: int):
    return 200, Participant.objects.inactive().for_race_id(race_id)


@router.delete("/{id}", tags=["races"], response={204: None, 404: str})
def delete_race(request, id: int):
    try:
        Race.objects.get(id=id).delete()
        return 204
    except Race.DoesNotExist:
        return 404, "Race not found."
