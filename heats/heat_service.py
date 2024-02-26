from typing import List

from django.db.models import Count, Sum, Q

from heats.models import Heat
from participants.models import Participant, RelayTeam
from race.models import RaceType


class AutoSchedulerException(Exception):
    """
    Exception raised when there is an error when running the automatic scheduler.
    """

    pass


def auto_schedule_heats(race_id: int) -> None:
    """
    Automatically schedule participants into heats.
    Participants are scheduled by swim time, and heats are organized by start time.
    The slower (higher swim time) the earlier they need to start (earlier heat).
    :return: None
    """

    if len(check_auto_schedule_is_ready(race_id)) > 0:
        raise AutoSchedulerException("Auto Schedule is not ready!")

    heats = Heat.objects.for_race(race_id=race_id).all()

    race_type: RaceType
    for race_type in RaceType.objects.for_race(race_id=race_id).distinct():
        race_type_heats = filter(
            lambda _heat: _heat.race_type_id == race_type.id, heats
        )
        total_count = 0
        for heat in race_type_heats:
            participant_ids = (
                Participant.objects.for_race_id(race_id)
                .active()
                .filter(race_type_id=race_type.id)
                .order_by("-swim_time")[total_count : total_count + heat.ideal_capacity]
                .values_list("id", flat=True)
            )

            relay_team_ids = (
                RelayTeam.objects.for_race_id(race_id)
                .active()
                .filter(race_type_id=race_type.id)[
                    total_count : total_count + heat.ideal_capacity
                ]
                .values_list("id", flat=True)
            )

            if len(participant_ids) != 0 and len(relay_team_ids) != 0:
                raise AutoSchedulerException(
                    "Participants and Relay Teams found for {} type".format(
                        race_type.__str__()
                    )
                )

            if len(participant_ids) > 0:
                Participant.objects.filter(id__in=participant_ids).update(heat=heat)
            elif len(relay_team_ids) > 0:
                RelayTeam.objects.filter(id__in=relay_team_ids).update(heat=heat)

            total_count += heat.ideal_capacity


def check_auto_schedule_is_ready(race_id: int) -> List[str]:
    """
    For the auto scheduler to be ready, it must have enough spaces for all its participants based on
    heat's ideal capacity.
    :return: Empty list if ready, list of error messages if issues are found.
    """

    errors = []

    # [{'race_type': int, 'max_capacity': int}]
    heat_list = (
        Heat.objects.for_race(race_id)
        .values("race_type")
        .annotate(max_capacity=Sum("ideal_capacity"))
    )

    heat_dict_capacity = {
        heat.get("race_type"): heat.get("max_capacity") for heat in heat_list
    }

    race_type: RaceType
    for race_type in RaceType.objects.for_race(race_id=race_id).annotate(
        count=Count("participants__bib_number", filter=Q(is_active=True))
        + Count("relay_teams__bib_number", filter=Q(is_active=True))
    ):
        if race_type.id not in heat_dict_capacity:
            errors.append("Race Type {} has no heats available".format(race_type.name))

        elif race_type.count > heat_dict_capacity[race_type.id]:
            errors.append(
                "Race Type {} does not have enough capacity. It has {} spots, it needs {} spots. {} spots are missing.".format(
                    race_type.name,
                    heat_dict_capacity[race_type.id],
                    race_type.count,
                    race_type.count - heat_dict_capacity[race_type.id],
                )
            )

    return errors
