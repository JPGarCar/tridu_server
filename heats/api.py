from typing import List

from ninja import Router

from heats.models import Heat
from heats.schema import HeatSchema, CreateHeatSchema, PatchHeatSchema
from tridu_server.schemas import ErrorObjectSchema

router = Router()


@router.get("/race/{race_id}", tags=["heats"], response={200: List[HeatSchema]})
def get_heats_for_race(request, race_id: int):
    return (
        200,
        Heat.objects.filter(race_id=race_id).select_related("race", "race_type").all(),
    )


@router.get(
    "/{heat_id}", tags=["heats"], response={200: HeatSchema, 404: ErrorObjectSchema}
)
def get_heat(request, heat_id: int):
    try:
        return 200, Heat.objects.get(id=heat_id)
    except Heat.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="Heat with id {} does not exist".format(heat_id)
        )


@router.patch(
    "/{heat_id}", tags=["heats"], response={200: HeatSchema, 404: ErrorObjectSchema}
)
def update_heat(request, heat_id: int, heat_schema: PatchHeatSchema):
    try:
        heat = Heat.objects.get(id=heat_id)
    except Heat.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="Heat with id {} does not exist".format(heat_id)
        )

    for key, value in heat_schema.dict().items():
        setattr(heat, key, value)

    heat.save()
    return 200, heat


@router.post("/", tags=["heats"], response={201: HeatSchema, 200: HeatSchema})
def create_heat(request, heat_schema: CreateHeatSchema):
    data = heat_schema.dict()

    race_id = data.pop("race", None)
    race_type_id = data.pop("race_type", None)

    data["race_id"] = race_id
    data["race_type_id"] = race_type_id

    heat, created = Heat.objects.get_or_create(**data)

    if created:
        return 201, heat
    else:
        return 200, heat


@router.delete(
    "/{heat_id}", tags=["heats"], response={204: None, 404: ErrorObjectSchema}
)
def delete_heat(request, heat_id: int):
    num_deleted, deleted = Heat.objects.filter(id=heat_id).delete()
    if num_deleted > 0:
        return 204
    else:
        return 404, ErrorObjectSchema.from_404_error(
            details="Heat with id {} does not exist".format(heat_id)
        )
