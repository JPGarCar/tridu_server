from typing import List

from ninja import Router

from participants.models import Participant, ParticipantComment
from participants.schema import ParticipantSchema, ParticipantCommentSchema

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
