from typing import List

from ninja import Router

from race.models import RaceType, Race
from race.schema import RaceTypeSchema, RaceSchema, CreateRaceSchema

router = Router()


@router.get("/racetypes", tags=["racetypes"], response={200: List[RaceTypeSchema]})
def get_race_types(request):
    return 200, RaceType.objects.filter(is_active=True).all()


@router.post("/racetypes", tags=["racetypes"], response={201: RaceTypeSchema})
def create_race_type(request, race_type_schema: RaceTypeSchema):
    race_type, isNew = RaceType.objects.get_or_create(**race_type_schema.dict())
    return 201, race_type


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


@router.delete("/{id}", tags=["races"], response={204: None, 404: str})
def delete_race(request, id: int):
    try:
        race = Race.objects.get(id=id)
        race.delete()
        return 204
    except Race.DoesNotExist:
        return 404, "Race not found."
