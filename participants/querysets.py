from __future__ import annotations

import datetime
from typing import List

from django.db.models import QuerySet, Count, Q


class BaseParticipantQuerySet(QuerySet):
    def of_user(self, user_id: int) -> BaseParticipantQuerySet:
        return self.filter(user_id=user_id)

    def active(self) -> BaseParticipantQuerySet:
        return self.filter(is_active=True)

    def inactive(self) -> BaseParticipantQuerySet:
        return self.filter(is_active=False)

    def order_by_most_recently_edited(self) -> BaseParticipantQuerySet:
        return self.order_by("-date_changed")


class ParticipantQuerySet(BaseParticipantQuerySet):
    def with_invalid_swim_time(self) -> ParticipantQuerySet:
        return self.filter(
            Q(swim_time__isnull=True)
            | Q(swim_time=datetime.timedelta(minutes=0, seconds=0))
        )

    def for_race_id(self, race_id: int) -> ParticipantQuerySet:
        return self.filter(
            race_id=race_id,
        )

    def in_heat(self, heat_id: int) -> ParticipantQuerySet:
        return self.filter(heat_id=heat_id)

    def not_in_race_types(self, heat_types: List[int]) -> ParticipantQuerySet:
        return self.exclude(race_type__in=heat_types)

    def active_for_race_grouped_by_race_type_and_ftt_count(
        self, race_id
    ) -> ParticipantQuerySet:

        return (
            self.for_race_id(race_id)
            .active()
            .values("race_type", "is_ftt")
            .annotate(count=Count("id"))
        )

    def active_for_race_grouped_by_race_type_count(
        self, race_id
    ) -> ParticipantQuerySet:

        return (
            self.for_race_id(race_id)
            .active()
            .values("race_type")
            .annotate(count=Count("id"))
        )

    def select_all_related(self) -> ParticipantQuerySet:
        return self.select_related("origin", "race", "race_type", "user", "heat")


class RelayParticipantQuerySet(BaseParticipantQuerySet):

    def select_all_related(self) -> RelayParticipantQuerySet:
        return self.select_related(
            "team",
            "team__heat",
            "team__race",
            "team__race_type",
        )


class RelayTeamQuerySet(QuerySet):

    def active(self) -> BaseParticipantQuerySet:
        return self.filter(is_active=True)

    def inactive(self) -> BaseParticipantQuerySet:
        return self.filter(is_active=False)

    def for_race_id(self, race_id: int) -> RelayTeamQuerySet:
        return self.filter(race_id=race_id)

    def for_heat(self, heat_id: int) -> RelayTeamQuerySet:
        return self.filter(heat_id=heat_id)

    def active_for_race_grouped_by_race_type_count(
        self, race_id
    ) -> ParticipantQuerySet:

        return (
            self.for_race_id(race_id)
            .active()
            .values("race_type")
            .annotate(count=Count("id"))
        )

    def select_all_related(self) -> ParticipantQuerySet:
        return self.select_related("race", "race_type", "heat")
