from typing import List

from ninja import Router
from ninja.pagination import paginate

from participants.models import ParticipantComment, RelayTeamComment
from participants.schema.particiapnt import ParticipantCommentSchema
from tridu_server.schemas import ErrorObjectSchema

participant_comment_router = Router()


@participant_comment_router.get(
    "/",
    tags=["comment", "participant"],
    response={200: List[ParticipantCommentSchema]},
)
@paginate
def get_all_participant_comments(request):
    return ParticipantComment.objects.all()


@participant_comment_router.delete(
    "/{comment_id}",
    tags=["comment", "participant"],
    response={204: None, 404: ErrorObjectSchema},
)
def delete_participant_comment(request, comment_id: int):

    try:
        ParticipantComment.objects.get(id=comment_id).delete()
        return 204, None
    except ParticipantComment.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Could not find comment to delete."
        )


relay_team_comment_router = Router()


@relay_team_comment_router.delete(
    "/{comment_id}",
    tags=["comment", "relay team"],
    response={204: None, 404: ErrorObjectSchema},
)
def delete_relay_team_comment(request, comment_id: int):
    try:
        RelayTeamComment.objects.get(id=comment_id).delete()
        return 204, None
    except ParticipantComment.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Could not find comment to delete."
        )
