from typing import List

from ninja import Router
from ninja.pagination import paginate

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


@router.get("/active/non-staff", response={201: List[UserSchema]})
@paginate
def get_active_non_staff_users(request):
    return 201, User.objects.exclude(is_staff=False, is_active=False)
