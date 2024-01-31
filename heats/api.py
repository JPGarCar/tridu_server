from typing import List

from django.contrib.sessions.models import Session
from ninja import Router

from heats.models import Heat
from race.schema import RaceSchema

router = Router()


@router.get("/race/{race_id}", tags=["heats"], response={200: List[RaceSchema]})
def get_heats_for_race(request, race_id: int):
    heats = Heat.objects.filter(race_id=race_id).all()
    return 200, heats
