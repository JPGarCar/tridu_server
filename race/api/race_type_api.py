from typing import List

from ninja import Router

from checkins.models import CheckIn
from race.models import RaceType
from race.schema import RaceTypeSchema, CreateRaceTypeSchema, PatchRaceTypeSchema
from tridu_server.schemas import ErrorObjectSchema

router = Router()


@router.delete(
    "/{race_type_id}",
    tags=["race type"],
    response={204: None, 404: ErrorObjectSchema},
)
def delete_race(request, race_type_id: int):
    try:
        race = RaceType.objects.get(id=race_type_id)
        race.delete()
        return 204, None
    except RaceType.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="RaceType with id {} does not exist".format(race_type_id)
        )


@router.patch(
    "/{race_type_id}",
    tags=["race type"],
    response={201: RaceTypeSchema, 404: ErrorObjectSchema},
)
def update_race_type(request, race_type_id: int, race_type_schema: PatchRaceTypeSchema):

    try:
        race_type = RaceType.objects.get(id=race_type_id)
    except RaceType.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "RaceType with id {} does not exist".format(race_type_id)
        )

    data = race_type_schema.dict(exclude_unset=True)

    if "checkins" in data:
        checkins = data.pop("checkins")
        request_checkin_ids = [checkin.get("id") for checkin in checkins]

        current_checkin_ids = race_type.checkins.values_list("id", flat=True)
        removed_checkin_ids = [
            current_checkin_id
            for current_checkin_id in current_checkin_ids
            if current_checkin_id not in request_checkin_ids
        ]
        to_add_checkins = CheckIn.objects.filter(id__in=request_checkin_ids)
        to_remove_checkins = CheckIn.objects.filter(id__in=removed_checkin_ids)
        race_type.checkins.add(*to_add_checkins)
        race_type.checkins.remove(*to_remove_checkins)

    for key, value in data.items():
        setattr(race_type, key, value)

    race_type.save()
    return 201, race_type


@router.get("/", tags=["race type"], response={200: List[RaceTypeSchema]})
def get_race_types(request):
    return 200, RaceType.objects.filter(is_active=True).all()


@router.post(
    "/",
    tags=["race type"],
    response={201: RaceTypeSchema, 200: RaceTypeSchema},
)
def create_race_type(request, race_type_schema: CreateRaceTypeSchema):
    race_type, created = RaceType.objects.get_or_create(**race_type_schema.dict())
    if created:
        return 201, race_type
    else:
        return 200, race_type
