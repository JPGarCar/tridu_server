from django.utils import timezone
from ninja import Router

from heats.models import Heat
from participants.models import Participant, RelayTeam
from tridu_server.schemas import ErrorObjectSchema
from wetbags.models import Wetbag
from wetbags.repository import get_wetbag, save_wetbag, update_wetbag, save_heats
from wetbags.schemas import WetbagSchema, CreateWetbagSchema, UpdateWetbagSchema

router = Router()


@router.post(
    "/", tags=["wetbags"], response={200: WetbagSchema, 404: ErrorObjectSchema}
)
def create_participant_wetbag(request, wetbag_schema: CreateWetbagSchema):
    wetbag_data = wetbag_schema.dict()

    try:
        Participant.objects.get(
            id=wetbag_data.get("participant_id"),
            user_id=wetbag_data.get("user_id"),
            bib_number=wetbag_data.get("bib_number"),
        )
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with the provided information does not exist."
        )

    wetbag = Wetbag(**wetbag_data)
    save_wetbag(wetbag)

    return 200, wetbag


@router.patch(
    "/{str:wetbag_id}/update",
    tags=["wetbags"],
    response={200: WetbagSchema, 404: ErrorObjectSchema},
)
def update_participant_wetbag(
    request, wetbag_id: str, wetbag_schema: UpdateWetbagSchema
):
    wetbag_data = wetbag_schema.dict(exclude_unset=True)

    wetbag = get_wetbag(wetbag_id)

    if wetbag is None:
        return 404, ErrorObjectSchema.from_404_error(
            "Wetbag with the provided information does not exist."
        )

    current_values = wetbag.to_dict()
    changed_values = {
        key: value
        for key, value in wetbag_data.items()
        if value != current_values.get(key, "")
    }

    if len(changed_values.keys()) == 0:
        return 200, wetbag

    changed_values["changed_datetime"] = timezone.now()

    if (
        "status" in changed_values.keys()
        and changed_values["status"] == Wetbag.WetbagStatus.REQUESTED
    ):
        changed_values["requested_datetime"] = timezone.now()

    for key, value in changed_values.items():
        setattr(wetbag, key, value)

    result = update_wetbag(wetbag_id, Wetbag.changed_to_dict(changed_values))

    if result is None:
        return 404, ErrorObjectSchema.from_404_error(
            "Wetbag with the provided information does not exist."
        )

    return 200, wetbag


@router.post(
    "/heats/transfer/{race_id}", tags=["wetbags", "heats"], response={200: int}
)
def transfer_heats_to_wetbag_system(request, race_id: int):
    heats = Heat.objects.for_race(race_id=race_id).all()

    save_heats(heats=heats)

    return 200, len(heats)


@router.get(
    "/relay_team/{int:relay_team_id}/can_have_wetbag",
    tags=["wetbags"],
    response={200: bool, 404: ErrorObjectSchema},
)
def can_relay_team_have_wetbag(request, relay_team_id: int):
    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    if relay_team.heat_id is not None:
        return 200, True

    return 200, False


@router.get(
    "/relay_team/{int:relay_team_id}",
    tags=["wetbags"],
    response={200: WetbagSchema, 404: ErrorObjectSchema, 409: ErrorObjectSchema},
)
def get_relay_team_wetbag(request, relay_team_id: int):
    try:
        relay_team = RelayTeam.objects.get(id=relay_team_id)
    except RelayTeam.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Relay Team with id {} does not exist".format(relay_team_id)
        )

    if relay_team.heat_id is None:
        return 409, ErrorObjectSchema.for_validation_error(
            "Having a Heat is required to have a WetBag.", "Relay Team"
        )

    wetbag_id = Wetbag.create_id(
        participant_id=relay_team_id,
        race_id=relay_team.race_id,
        bib_number=relay_team.bib_number,
        heat_id=relay_team.heat_id,
    )

    wetbag = get_wetbag(wetbag_id=wetbag_id)

    if wetbag is None:
        wetbag = Wetbag(
            participant_id=relay_team_id,
            race_id=relay_team.race_id,
            bib_number=relay_team.bib_number,
            changed_datetime=timezone.now(),
            heat_id=relay_team.heat_id,
            color=relay_team.heat.color,
        )
        save_wetbag(wetbag)

    return 200, wetbag


@router.get(
    "/{int:participant_id}/can_have_wetbag",
    tags=["wetbags"],
    response={200: bool, 404: ErrorObjectSchema},
)
def can_participant_have_wetbag(request, participant_id: int):
    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    if participant.heat_id is not None:
        return 200, True

    return 200, False


@router.get(
    "/{int:participant_id}",
    tags=["wetbags"],
    response={200: WetbagSchema, 404: ErrorObjectSchema, 409: ErrorObjectSchema},
)
def get_participant_wetbag(request, participant_id: int):
    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return 404, ErrorObjectSchema.from_404_error(
            "Participant with id {} does not exist".format(participant_id)
        )

    if participant.heat_id is None:
        return 409, ErrorObjectSchema.for_validation_error(
            "Having a Heat is required to have a WetBag.", "Participant"
        )

    wetbag_id = Wetbag.create_id(
        participant_id=participant_id,
        race_id=participant.race_id,
        bib_number=participant.bib_number,
        heat_id=participant.heat_id,
    )

    wetbag = get_wetbag(wetbag_id=wetbag_id)

    if wetbag is None:
        wetbag = Wetbag(
            participant_id=participant_id,
            race_id=participant.race_id,
            bib_number=participant.bib_number,
            changed_datetime=timezone.now(),
            heat_id=participant.heat_id,
            color=participant.heat.color,
        )
        save_wetbag(wetbag)

    return 200, wetbag
