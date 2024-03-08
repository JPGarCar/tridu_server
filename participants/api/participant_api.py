import datetime
from typing import List

from django.core.exceptions import ValidationError
from ninja import Router

from checkins.models import CheckIn
from heats.models import Heat
from locations.models import Location
from participants.api.comment_api import participant_comment_router
from participants.models import Participant, ParticipantComment, ParticipantCheckIn
from participants.schema.particiapnt import (
    ParticipantSchema,
    ParticipantCommentSchema,
    ParticipantCommentCreateSchema,
    PatchParticipantSchema,
    CreateParticipantBulkSchema,
)
from race.models import RaceType
from race.schema import RaceTypeSchema
from tridu_server.schemas import BulkCreateResponseSchema, ErrorObjectSchema

router = Router()

router.add_router("/comments", participant_comment_router)


@router.post("/import", tags=["import"], response={201: BulkCreateResponseSchema})
def create_participant_bulk(
    request, participantSchemas: List[CreateParticipantBulkSchema]
):
    created = 0
    duplicates = 0
    errors = []
    items = []
    count = 2  # excel starts at 2

    for participantSchema in participantSchemas:
        data = participantSchema.dict()

        origin = None
        if "city" in data and "country" in data and "province" in data:
            # get origin of Participant
            city = data.pop("city")
            country = data.pop("country")
            province = data.pop("province")
            if province and country and city:
                origin, isNewOrigin = Location.objects.get_or_create(
                    city=city, country=country, province=province
                )

        try:
            swim_time_values = data.get("swim_time", "").strip().split(":")
            if len(swim_time_values) != 2:
                raise ValidationError("Invalid swim_time, not in formation MM:SS")
            minutes = swim_time_values[0]
            seconds = swim_time_values[1]
            if not minutes.isnumeric() or not seconds.isnumeric():
                raise ValidationError("Invalid swim_time, not in formation MM:SS")
            swim_time = datetime.timedelta(seconds=int(seconds), minutes=int(minutes))

            try:
                participant = Participant.objects.get(
                    bib_number=data["bib_number"],
                    race_id=data["race"],
                    race_type_id=data["race_type"],
                    user_id=data["user"],
                )
                participant.swim_time = swim_time
                participant.location = data.get("location", "")
                participant.team = data.get("team", "")
                participant.origin_id = origin.id if origin is not None else None
                participant.save()
                duplicates += 1
            except Participant.DoesNotExist:
                participant = Participant.objects.create(
                    origin_id=origin.id if origin is not None else None,
                    bib_number=data["bib_number"],
                    is_ftt=data["is_ftt"],
                    team=data.get("team", ""),
                    swim_time=swim_time,
                    race_id=data["race"],
                    race_type_id=data["race_type"],
                    user_id=data["user"],
                    location=data.get("location", ""),
                )
                created += 1
            items.append(ParticipantSchema.from_orm(participant).model_dump_json())
        except Exception as e:
            errors.append("For row {}, error {}".format(count, e.__str__()))

        count = count + 1

    return 201, {
        "created": created,
        "duplicates": duplicates,
        "errors": errors,
        "items": items,
        "message": (
            "{} participants created, {} were already found, no errors encountered.".format(
                created, duplicates
            )
            if len(errors) == 0
            else "{} participants created, {} were already found but {} errors encountered!".format(
                created, duplicates, len(errors)
            )
        ),
    }


@router.get(
    "/recently_edited", tags=["participant"], response={200: List[ParticipantSchema]}
)
def recently_edited_participants(request, count: int = 5):
    """Returns the most recently edited participants."""
    return (
        200,
        Participant.objects.select_all_related()
        .order_by_most_recently_edited()
        .all()[:count],
    )


@router.patch(
    "/{participant_id}/reactivate",
    tags=["participant"],
    response={201: ParticipantSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def reactivate_participant(request, participant_id: int):

    try:
        participant = Participant.objects.select_all_related().get(id=participant_id)
        participant.activate()
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    try:
        participant.validate_constraints()
        participant.save()
        return 201, participant
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(e, "Participant")


@router.patch(
    "/{participant_id}/change_race_type",
    tags=["participant"],
    response={201: ParticipantSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def change_participant_race_type(
    request, participant_id: int, race_type_schema: RaceTypeSchema
):

    try:
        participant = Participant.objects.select_all_related().get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    if participant.heat:
        return (
            409,
            ErrorObjectSchema.for_validation_error(
                instance_name="Participant",
                details="Participant is in a heat. Please remove them from their heat first.",
            ),
        )

    try:
        new_race_type = RaceType.objects.get(id=race_type_schema.id)
    except RaceType.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Race Type with id {} does not exist".format(race_type_schema.id)
        )

    participant.race_type = new_race_type
    participant.save()

    return 201, participant


@router.patch(
    "/{participant_id}/change_heat/{heat_id}",
    tags=["participant"],
    response={200: ParticipantSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def change_participant_heat(request, participant_id: int, heat_id: int):

    try:
        participant = Participant.objects.select_all_related().get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    if participant.heat:
        return (
            409,
            ErrorObjectSchema.for_validation_error(
                instance_name="Participant",
                details="Participant is in a Heat. Please remove them from their Heat first.",
            ),
        )

    if not participant.is_active:
        return 409, ErrorObjectSchema.for_validation_error(
            instance_name="Participant",
            details="Participant is in an inactive state. Unable to add to Heat.",
        )

    try:
        new_heat = Heat.objects.get(id=heat_id)
    except Heat.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Heat with id {} does not exist".format(heat_id)
        )

    if new_heat.race_type_id != participant.race_type_id:
        return 409, ErrorObjectSchema.for_validation_error(
            instance_name="Participant",
            details="Race Types do not match, Participant is {} and Heat is {}".format(
                participant.race_type.name, new_heat.race_type.name
            ),
        )

    participant.heat = new_heat
    participant.save()

    return 200, participant


@router.patch(
    "/{participant_id}/remove_heat",
    tags=["participant"],
    response={201: ParticipantSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def remove_participant_heat(request, participant_id: int):

    try:
        participant = Participant.objects.select_all_related().get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    if not participant.heat:
        return (
            409,
            ErrorObjectSchema.for_validation_error(
                instance_name="Participant",
                details="Participant is not in a heat. Cannot remove from a heat.",
            ),
        )

    participant.heat = None
    participant.save()

    return 201, participant


@router.patch(
    "/{participant_id}/deactivate",
    tags=["participant"],
    response={201: ParticipantSchema, 404: ErrorObjectSchema},
)
def deactivate_participant(request, participant_id: int):

    try:
        participant = Participant.objects.select_all_related().get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    participant.deactivate()
    participant.save()
    return 201, participant


@router.patch(
    "{participant_id}/checkins/{checkin_id}",
    tags=["participant", "checkins"],
    response={200: ParticipantSchema, 404: ErrorObjectSchema, 409: ErrorObjectSchema},
)
def checkin_participant(
    request, participant_id: int, checkin_id: int, value: bool = None
):
    """By default, it will flip the value, but if value is in URL, set that value."""

    try:
        participant = Participant.objects.select_all_related().get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    try:
        checkin = CheckIn.objects.select_related(
            "depends_on", "depends_on__depends_on", "depends_on__depends_on__depends_on"
        ).get(id=checkin_id)
    except CheckIn.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "CheckIn with id {} does not exist".format(checkin_id)
        )

    if checkin.depends_on is not None:
        not_ready = False
        participant_dependent = None
        try:
            participant_dependent = participant.checkins.get(
                check_in__id=checkin.depends_on.id
            )
        except ParticipantCheckIn.DoesNotExist:
            not_ready = True

        if not_ready or not participant_dependent.is_checked_in:
            return 409, ErrorObjectSchema.for_validation_error(
                "Can not check in participant to {} as they have not checked in at {}".format(
                    checkin.name, checkin.depends_on.name
                ),
                "Participant",
            )

    try:
        participant_checkin = participant.checkins.get(check_in__id=checkin_id)
    except ParticipantCheckIn.DoesNotExist:
        participant.checkins.create(
            check_in_id=checkin_id,
            is_checked_in=True,
        )
        participant.refresh_from_db()
        return 200, participant

    if value:
        participant_checkin.is_checked_in = value
    else:
        participant_checkin.is_checked_in = not participant_checkin.is_checked_in

    participant_checkin.save()
    participant.refresh_from_db()
    return 200, participant


@router.get(
    "/{participant_id}/comments",
    tags=["participant", "comment"],
    response={
        200: List[ParticipantCommentSchema],
    },
)
def get_participant_comments(request, participant_id: int):
    return 200, ParticipantComment.objects.filter(
        participant_id=participant_id
    ).select_related("writer")


@router.post(
    "/{participant_id}/comments",
    tags=["participant", "comment"],
    response={201: ParticipantCommentSchema, 409: ErrorObjectSchema},
)
def create_participant_comment(
    request, participant_id: int, commentSchema: ParticipantCommentCreateSchema
):
    comment = ParticipantComment(
        participant_id=participant_id,
        comment=commentSchema.comment,
        writer=request.user,
    )

    try:
        comment.validate_constraints()
        comment.save()
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error=e, instance_name="Participant Comment"
        )

    return 201, comment


@router.get(
    "/{participant_id}",
    tags=["participant"],
    response={200: ParticipantSchema, 404: ErrorObjectSchema},
)
def get_participant(request, participant_id: int):
    try:
        return 200, Participant.objects.select_all_related().get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )


@router.patch(
    "/{participant_id}",
    tags=["participant"],
    response={200: ParticipantSchema, 409: ErrorObjectSchema, 404: ErrorObjectSchema},
)
def update_participant(
    request, participant_id: int, participant_schema: PatchParticipantSchema
):
    try:
        participant = Participant.objects.select_all_related().get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    data = participant_schema.dict(exclude_unset=True)

    # update origin of Participant
    if "origin" in data:
        origin_data = data.pop("origin")
        if (
            "country" in origin_data
            and "province" in origin_data
            and "city" in origin_data
        ):
            origin = Location.objects.filter(
                country=origin_data["country"],
                province=origin_data["province"],
                city=origin_data["city"],
            ).first()
            if origin is None:
                origin = Location.objects.create(
                    country=origin_data["country"],
                    province=origin_data["province"],
                    city=origin_data["city"],
                )
            participant.origin = origin

    # update participant values
    for key, value in data.items():
        setattr(participant, key, value)

    try:
        participant.validate_constraints()
    except ValidationError as e:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error=e, instance_name="Participant"
        )

    participant.save()
    return 200, participant
