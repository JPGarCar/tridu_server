from typing import List

from ninja import Router

from race.models import RaceType, Race
from race.schema import RaceTypeSchema, RaceSchema

router = Router()


@router.get("/racetypes", tags=["racetypes"], response={200: List[RaceTypeSchema]})
def get_race_types(request):
    return 200, RaceType.objects.filter(is_active=True).all()


@router.get("/", tags=["races"], response={200: List[RaceSchema]})
def get_races(request):
    return 200, Race.objects.filter(is_active=True).all()
