from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from heats.models import Heat
from heats.schema import HeatSchema, CreateHeatSchema, PatchHeatSchema

router = Router()


@router.get("/race/{race_id}", tags=["heats"], response={200: List[HeatSchema]})
def get_heats_for_race(request, race_id: int):
    heats = (
        Heat.objects.filter(race_id=race_id).select_related("race", "race_type").all()
    )
    return 200, heats


@router.get("/{heat_id}", tags=["heats"], response={200: HeatSchema})
def get_heat(request, heat_id: int):
    return 200, get_object_or_404(Heat, id=heat_id)


@router.patch("/{heat_id}", tags=["heats"], response={201: HeatSchema})
def update_heat(request, heat_id: int, heatSchema: PatchHeatSchema):
    heat = get_object_or_404(Heat, id=heat_id)

    for key, value in heatSchema.dict().items():
        setattr(heat, key, value)

    heat.save()
    return 201, heat


@router.post("/", tags=["heats"], response={201: HeatSchema})
def create_heat(request, heat: CreateHeatSchema):
    data = heat.dict()

    race_id = data.pop("race", None)
    race_type_id = data.pop("race_type", None)

    data["race_id"] = race_id
    data["race_type_id"] = race_type_id

    new_heat = Heat.objects.create(**data)
    return 201, new_heat
