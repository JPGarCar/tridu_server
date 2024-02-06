from typing import List

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router

from heats.models import Heat
from heats.schema import HeatSchema
from locations.models import Location
from participants.models import Participant, ParticipantComment
from participants.schema import (
    ParticipantSchema,
    ParticipantCommentSchema,
    ParticipantCommentCreateSchema,
    PatchParticipantSchema,
    CreateParticipantSchema,
    CreateParticipantBulkSchema,
)
from race.models import RaceType
from race.schema import RaceTypeSchema
from tridu_server.schemas import BulkCreateResponseSchema

router = Router()


@router.post(
    "/user/{user_id}/participants",
    tags=["participants"],
    response={201: ParticipantSchema, 400: str},
)
def create_participant(
    request, user_id: int, participantSchema: CreateParticipantSchema
):
    data = participantSchema.dict(exclude_unset=True)

    # get origin of Participant
    origin_data = data.pop("origin")
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

    try:
        participant, created = Participant.objects.get_or_create(
            origin=origin,
            bib_number=data["bib_number"],
            is_ftt=data["is_ftt"],
            team=data["team"],
            swim_time=data["swim_time"],
            race_id=data["race"],
            race_type_id=data["race_type"],
            user_id=user_id,
        )
    except IntegrityError as error:
        return 400, error.__str__()

    return 201, participant


@router.get(
    "/user/{user_id}/participants",
    tags=["participants"],
    response={201: List[ParticipantSchema], 204: None},
)
def get_participants_for_user(request, user_id: int):
    participants = Participant.objects.filter(user_id=user_id).select_related(
        "origin", "race", "race_type"
    )

    if participants:
        return 201, participants
    else:
        return 204, None


@router.get(
    "/heat/{heat_id}",
    tags=["participants", "heats"],
    response={200: List[ParticipantSchema]},
)
def get_participants_for_heat(request, heat_id: int):
    participants = Participant.objects.filter(heat_id=heat_id)
    return 200, participants


@router.post("/bulk", tags=["participants"], response={201: BulkCreateResponseSchema})
def create_participant_bulk(
    request, participantSchemas: List[CreateParticipantBulkSchema]
):
    created = 0
    duplicates = 0
    errors = []
    items = []
    count = 1

    for participantSchema in participantSchemas:
        data = participantSchema.dict(exclude_unset=True)

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
            location = data.get("location", "")
            if location == "N/A" or location == "n/a":
                location = None
            participant, isNew = Participant.objects.get_or_create(
                origin_id=origin.id if origin is not None else None,
                bib_number=data["bib_number"],
                is_ftt=data["is_ftt"],
                team=data.get("team", ""),
                swim_time=data.get("swim_time", ""),
                race_id=data["race"],
                race_type_id=data["race_type"],
                user_id=data["user"],
                location=location,
            )

            if isNew:
                created += 1
            else:
                duplicates += 1

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


@router.patch(
    "/{participant_id}/reactivate",
    tags=["participants"],
    response={201: ParticipantSchema},
)
def reactivate_participant(request, participant_id: int):
    participant = get_object_or_404(Participant, pk=participant_id)
    participant.activate()
    participant.save()
    return 201, participant


@router.patch(
    "/{participant_id}/change_race_type",
    tags=["participants"],
    response={201: ParticipantSchema, 409: str},
)
def change_participant_race_type(
    request, participant_id: int, race_type: RaceTypeSchema
):
    participant = get_object_or_404(Participant, pk=participant_id)

    if participant.heat:
        return (
            409,
            "Participant is in a heat. Please remove them from their heat first.",
        )

    new_race_type = RaceType.objects.filter(id=race_type.id).first()

    if new_race_type is None:
        return (
            409,
            "Race Type provided does not exist!",
        )

    participant.race_type = new_race_type
    participant.save()

    return 201, participant


@router.patch(
    "/{participant_id}/change_heat",
    tags=["participants"],
    response={201: ParticipantSchema, 409: str},
)
def change_participant_heat(request, participant_id: int, heat: HeatSchema):
    participant = get_object_or_404(Participant, pk=participant_id)

    if participant.heat:
        return (
            409,
            "Participant is in a heat. Please remove them from their heat first.",
        )

    new_heat = Heat.objects.filter(id=heat.id).first()

    if new_heat is None:
        return (
            409,
            "Heat provided does not exist!",
        )

    participant.heat = new_heat
    participant.save()

    return 201, participant


@router.patch(
    "/{participant_id}/remove_heat",
    tags=["participants"],
    response={201: ParticipantSchema, 409: str},
)
def remove_participant_heat(request, participant_id: int):
    participant = get_object_or_404(Participant, pk=participant_id)

    if not participant.heat:
        return (
            409,
            "Participant is not in a heat",
        )

    participant.heat = None
    participant.save()

    return 201, participant


@router.patch(
    "/{participant_id}/deactivate",
    tags=["participants"],
    response={201: ParticipantSchema},
)
def deactivate_participant(request, participant_id: int):
    participant = get_object_or_404(Participant, pk=participant_id)
    participant.deactivate()
    participant.save()
    return 201, participant


@router.get(
    "/{participant_id}/comments",
    tags=["participants"],
    response={200: List[ParticipantCommentSchema], 204: None},
)
def get_participant_comments(request, participant_id: int):
    comments = ParticipantComment.objects.filter(participant_id=participant_id)

    if comments:
        return 200, comments
    else:
        return 204, None


@router.post(
    "/{participant_id}/comments", tags=["participants"], response={201: bool, 500: str}
)
def create_participant_comment(
    request, participant_id: int, commentSchema: ParticipantCommentCreateSchema
):
    comment = ParticipantComment.objects.create(
        participant_id=participant_id,
        comment=commentSchema.comment,
        writer=request.user,
    )

    if comment:
        return 201, True
    else:
        return 500, "There was an error creating a comment"


@router.patch(
    "/{participant_id}", tags=["participants"], response={201: ParticipantSchema}
)
def update_participant(
    request, participant_id: int, participantSchema: PatchParticipantSchema
):
    participant = get_object_or_404(Participant, pk=participant_id)

    data = participantSchema.dict(exclude_unset=True)

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

    participant.save()
    return 201, participant


@router.delete(
    "/comment/{comment_id}", tags=["participants"], response={200: None, 404: str}
)
def delete_participant_comment(request, comment_id: int):
    comment = get_object_or_404(ParticipantComment, pk=comment_id)

    if comment:
        comment.delete()
        return 200, None

    return 404, "Could not find comment to delete."
