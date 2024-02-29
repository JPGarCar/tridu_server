from typing import List

from django.core.exceptions import ValidationError
from ninja import Router

from checkins.models import CheckIn
from checkins.schema import CheckInSchema, CreateCheckInSchema, PatchCheckInSchema
from race.models import RaceType
from race.schema import RaceTypeSchema
from tridu_server.schemas import ErrorObjectSchema

router = Router()


@router.get("/", tags=["checkins"], response={200: List[CheckInSchema]})
def get_checkins(request):
    return 200, CheckIn.objects.all()


@router.post("/", tags=["checkins"], response={201: CheckInSchema})
def create_checkin(request, check_in_schema: CreateCheckInSchema):

    schema_data = check_in_schema.dict()

    depends_on = None
    if "depends_on" in schema_data:
        depends_on_schema = schema_data.pop("depends_on")
        if depends_on_schema:
            try:
                depends_on = CheckIn.objects.get(**depends_on_schema)
            except CheckIn.DoesNotExist:
                return 404, ErrorObjectSchema.from_404_error(
                    "Check In used as a dependency with ID {} does not exist.".format(
                        depends_on_schema.get("id")
                    )
                )

    check_in, is_new = CheckIn.objects.get_or_create(
        **schema_data, depends_on=depends_on
    )
    if is_new:
        return 201, check_in
    else:
        return 200, check_in


@router.get(
    "/{check_in_id}/race_types", tags=["checkins"], response={200: List[RaceTypeSchema]}
)
def get_check_in_race_types(request, check_in_id: int):
    return 200, RaceType.objects.filter(checkins__in=[check_in_id]).all()


@router.delete(
    "/{check_in_id}", tags=["checkins"], response={204: None, 404: ErrorObjectSchema}
)
def delete_checkin(request, check_in_id: int):
    try:
        check_in = CheckIn.objects.get(id=check_in_id)
        check_in.delete()
        return 204, None
    except CheckIn.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "CheckIn with id {} does not exist".format(check_in_id)
        )


@router.patch(
    "/{check_in_id}",
    tags=["checkins"],
    response={200: CheckInSchema, 404: ErrorObjectSchema},
)
def update_checkin(request, check_in_id: int, check_in_schema: PatchCheckInSchema):
    try:
        check_in = CheckIn.objects.get(id=check_in_id)
    except CheckIn.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "CheckIn with id {} does not exist".format(check_in_id)
        )

    check_in_data = check_in_schema.dict(exclude_unset=True)

    # update Check In values
    for key, value in check_in_data.items():
        setattr(check_in, key, value)

    try:
        check_in.validate_constraints()
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error=e, instance_name="CheckIn"
        )

    check_in.save()
    return 200, check_in


@router.get(
    "/{check_in_id}",
    tags=["checkins"],
    response={200: CheckInSchema, 404: ErrorObjectSchema},
)
def get_checkin(request, check_in_id: int):
    try:
        return 200, CheckIn.objects.get(id=check_in_id)
    except CheckIn.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "CheckIn with id {} does not exist".format(check_in_id)
        )
