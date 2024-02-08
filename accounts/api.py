from typing import List

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from accounts.models import User
from accounts.schema import UserSchema, PatchUserSchema, CreateUserSchema
from tridu_server.schemas import BulkCreateResponseSchema

router = Router()


@router.get("/active/non-staff", response=List[UserSchema])
@paginate
def get_active_non_staff_users(request, name: str = ""):
    if name != "":
        queryset = User.objects.filter(is_staff=False, is_active=True)
        for term in name.split():
            queryset = queryset.filter(
                Q(first_name__icontains=term) | Q(last_name__icontains=term)
            )
        users = queryset.order_by("first_name", "last_name").all()
        return users
    users = (
        User.objects.exclude(Q(is_staff=True) | Q(is_active=False))
        .order_by("first_name", "last_name")
        .all()
    )
    return users


@router.get("/username/{username}", response={200: UserSchema, 404: str})
def get_user_by_username(request, username: str):
    try:
        user = User.objects.get(username=username)
        return 200, user
    except User.DoesNotExist:
        return 404, "User not found."


@router.post("/bulk", response={201: BulkCreateResponseSchema})
def create_users_bulk(request, userSchemas: List[CreateUserSchema]):

    created = 0
    duplicates = 0
    errors = []
    user_datas = []

    for userSchema in userSchemas:
        user_data = userSchema.dict()

        # create username
        username = (
            user_data.get("first_name", "").replace(" ", "").lower()
            + "."
            + user_data.get("last_name", "").replace(" ", "").lower()
        )

        try:
            try:
                user = User.objects.get(username=username)
                is_new = False
            except User.DoesNotExist:
                user = User.objects.create(
                    username=username,
                    email=user_data.get("email", ""),
                    first_name=user_data.get("first_name", ""),
                    last_name=user_data.get("last_name", ""),
                    phone_number=user_data.get("phone_number", ""),
                    date_of_birth=user_data.get("date_of_birth", ""),
                    gender=user_data.get("gender", None),
                )
                is_new = True

            if is_new:
                created += 1
            else:
                duplicates += 1

            user_datas.append(UserSchema.from_orm(user).model_dump_json())
        except Exception as e:
            errors.append(e.__str__())

    return 201, {
        "created": created,
        "duplicates": duplicates,
        "errors": errors,
        "items": user_datas,
        "message": (
            "{} users created, {} were already found, no errors encountered.".format(
                created, duplicates
            )
            if len(errors) == 0
            else "{} participants created, {} were already found but {} errors encountered!".format(
                created, duplicates, len(errors)
            )
        ),
    }


@router.post("/action/clean_gender", response={200: str, 403: str})
def admin_action_clean_gender(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return 403, "You must be an admin to access this action"

    num_updated = 0

    num_updated += User.objects.filter(gender__in=["W", "Woman", "Female"]).update(
        gender="F"
    )
    num_updated += User.objects.filter(gender__in=["Man", "Male", "Man"]).update(
        gender="M"
    )

    return 200, "Action complete, {} instances updated".format(num_updated)


@router.get("/{user_id}", response={200: UserSchema, 404: str})
def get_user_by_id(request, user_id: int) -> UserSchema:
    try:
        user = User.objects.get(id=user_id)
        return 200, user
    except User.DoesNotExist:
        return 404, "User not found."


@router.patch("/{user_id}", response={201: UserSchema})
def update_user(request, user_id: int, userSchema: PatchUserSchema):
    user = get_object_or_404(User, id=user_id)
    for key, value in userSchema.dict().items():
        setattr(user, key, value)
    user.save()
    return 201, user


@router.post("/", response={201: UserSchema})
def create_user(request, userSchema: CreateUserSchema):
    user_data = userSchema.dict()

    # create username
    username = (
        user_data.get("first_name", "").replace(" ", "").lower()
        + "."
        + user_data.get("last_name", "").replace(" ", "").lower()
    )

    # try to find user by username
    user = User.objects.filter(username=username).first()

    if user is None:
        user = User.objects.create_user(
            username=username,
            email=user_data.get("email", ""),
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            phone_number=user_data.get("phone_number", ""),
            date_of_birth=user_data.get("date_of_birth", ""),
            gender=user_data.get("gender", None),
        )

    return 201, user
