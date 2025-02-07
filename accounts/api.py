from typing import List

from django.core.exceptions import ValidationError
from django.db.models import Q
from ninja import Router
from ninja.pagination import paginate

from accounts.models import User
from accounts.schema import UserSchema, PatchUserSchema, CreateUserSchema
from locations.models import Location
from participants.models import Participant, RelayParticipant
from participants.schema.particiapnt import (
    ParticipantSchema,
    ParticipationSchema,
    CreateParticipantSchema,
)
from tridu_server.schemas import BulkCreateResponseSchema, ErrorObjectSchema

router = Router()


@router.get("/active/non-staff", tags=["user"], response=List[UserSchema])
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


@router.post(
    "/import", tags=["user", "import"], response={201: BulkCreateResponseSchema}
)
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
                user = User.objects.get(username=username, email=user_data.get("email"))
                user.phone_number = user_data.get("phone_number", "")
                user.date_of_birth = user_data.get("date_of_birth", "")
                user.gender = user_data.get("gender", None)
                user.save()
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


@router.post(
    "/action/clean_gender",
    tags=["user", "admin action"],
    response={200: str, 403: ErrorObjectSchema},
)
def admin_action_clean_gender(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return 403, ErrorObjectSchema(
            title="Permission Denied",
            status=403,
            details="You do not have permission to perform this action. You must be an admin!",
        )

    num_updated = 0

    num_updated += User.objects.filter(gender__in=["W", "Woman", "Female"]).update(
        gender="F"
    )
    num_updated += User.objects.filter(gender__in=["Man", "Male", "Man"]).update(
        gender="M"
    )

    return 200, "Action complete, {} instances updated".format(num_updated)


@router.get(
    "/{int:user_id}/participations",
    tags=["user"],
    response={200: List[ParticipationSchema]},
)
def get_user_participations(request, user_id: int):
    participations = []

    participant: Participant
    for participant in Participant.objects.of_user(user_id).all():
        participations.append(
            ParticipationSchema(
                id=participant.id,
                race=participant.race,
                type=ParticipationSchema.ParticipationTypes.PARTICIPANT,
                user=participant.user,
                bib_number=participant.bib_number,
            )
        )

    relay_participant: RelayParticipant
    for relay_participant in RelayParticipant.objects.of_user(user_id):
        participations.append(
            ParticipationSchema(
                id=relay_participant.id,
                race=relay_participant.team.race,
                type=ParticipationSchema.ParticipationTypes.RELAY_PARTICIPANT,
                user=relay_participant.user,
                bib_number=relay_participant.team.bib_number,
            )
        )

    return 200, participations


@router.post(
    "/{user_id}/participants",
    tags=["participant", "user"],
    response={201: ParticipantSchema, 409: ErrorObjectSchema},
)
def create_user_participant(
    request, user_id: int, participantSchema: CreateParticipantSchema
):
    data = participantSchema.dict()

    # get origin of Participant
    origin = None
    if "origin" in data:
        origin_data = data.pop("origin")
        country = origin_data["country"]
        province = origin_data["province"]
        city = origin_data["city"]

        if country and province and city:
            try:
                origin = Location.objects.get(
                    country=country, province=province, city=city
                )
            except Location.DoesNotExist:
                origin = None
        else:
            origin = None

    try:
        participant = Participant(
            origin=origin,
            bib_number=data["bib_number"],
            is_ftt=data["is_ftt"],
            team=data["team"],
            swim_time=data["swim_time"],
            race_id=data["race"],
            race_type_id=data["race_type"],
            user_id=user_id,
        )
        participant.validate_constraints()
        participant.save()

        return 201, participant
    except ValidationError as validation_error:
        return 409, ErrorObjectSchema.from_validation_error(
            validation_error, "Participant"
        )


@router.get(
    "/{user_id}/participants",
    tags=["participant", "user"],
    response={200: List[ParticipantSchema]},
)
def get_user_participants(request, user_id: int):
    participants = Participant.objects.of_user(user_id).select_all_related()
    return 200, participants


@router.get(
    "/{int:user_id}", tags=["user"], response={200: UserSchema, 404: ErrorObjectSchema}
)
def get_user_by_id(request, user_id: int):
    try:
        return 200, User.objects.get(id=user_id)
    except User.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="User with id {} does not exist".format(user_id)
        )


@router.get(
    "/{str:username}", tags=["user"], response={200: UserSchema, 404: ErrorObjectSchema}
)
def get_user_by_username(request, username: str):
    try:
        return 200, User.objects.get(username=username)
    except User.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="User with username {} does not exist".format(username)
        )


@router.patch(
    "/{int:user_id}", tags=["user"], response={201: UserSchema, 404: ErrorObjectSchema}
)
def update_user(request, user_id: int, userSchema: PatchUserSchema):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            details="User with id {} does not exist".format(user_id)
        )

    for key, value in userSchema.dict(exclude_unset=True).items():
        setattr(user, key, value)
    user.save()
    return 201, user


@router.post("/", tags=["user"], response={201: UserSchema, 200: UserSchema})
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

    return 200, user
