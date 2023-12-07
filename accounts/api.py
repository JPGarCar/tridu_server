from ninja import Router

from accounts.models import User
from accounts.schema import UserSchema

router = Router()


@router.get("/{username}", response={201: UserSchema, 204: None})
def get_user_by_username(request, username: str):
    try:
        user = User.objects.get(username=username)
        return 201, user
    except User.DoesNotExist:
        return 204, None
