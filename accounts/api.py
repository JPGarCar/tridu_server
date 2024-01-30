from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from accounts.models import User
from accounts.schema import UserSchema, PatchUserSchema

router = Router()


@router.get("/{user_id}", response={201: UserSchema, 204: None})
def get_user_by_id(request, user_id: int) -> UserSchema:
    try:
        user = User.objects.get(id=user_id)
        return 201, user
    except User.DoesNotExist:
        return 204, None


@router.get("/username/{username}", response={201: UserSchema, 204: None})
def get_user_by_username(request, username: str):
    try:
        user = User.objects.get(username=username)
        return 201, user
    except User.DoesNotExist:
        return 204, None


@router.patch("/{user_id}", response={201: UserSchema})
def update_user(request, user_id: int, userSchema: PatchUserSchema):
    user = get_object_or_404(User, id=user_id)
    for key, value in userSchema.dict().items():
        setattr(user, key, value)
    user.save()
    return 201, user


@router.get("/active/non-staff", response={201: List[UserSchema]})
@paginate
def get_active_non_staff_users(request):
    return 201, User.objects.exclude(is_staff=False, is_active=False)
