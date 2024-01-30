from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router, Form

from locations.models import Location
from participants.models import Participant, ParticipantComment
from participants.schema import (
    ParticipantSchema,
    ParticipantCommentSchema,
    ParticipantCommentCreateSchema,
    PatchParticipantSchema,
)

router = Router()


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
        origin_data = data.pop("origin", None)
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
