from typing import List

from ninja import Router

from race.models import RaceType
from race.schema import RaceTypeSchema, CreateRaceTypeSchema
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
        return 204
    except RaceType.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="RaceType with id {} does not exist".format(race_type_id)
        )


@router.patch(
    "/{race_type_id}",
    tags=["race type"],
    response={201: RaceTypeSchema, 404: ErrorObjectSchema},
)
def update_race_type(
    request, race_type_id: int, race_type_schema: CreateRaceTypeSchema
):

    try:
        race_type = RaceType.objects.get(id=race_type_id)
    except RaceType.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "RaceType with id {} does not exist".format(race_type_id)
        )

    for key, value in race_type_schema.dict().items():
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
