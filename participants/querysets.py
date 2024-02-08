from __future__ import annotations

import datetime

from django.db.models import QuerySet, Count, Q


class ParticipantQuerySet(QuerySet):
    def with_invalid_swim_time(self) -> ParticipantQuerySet:
        return self.filter(
            Q(swim_time__isnull=True)
            | Q(swim_time=datetime.timedelta(minutes=0, seconds=0))
        )

    def for_race_id(self, race_id: int) -> ParticipantQuerySet:
        return self.filter(
            race_id=race_id,
        )

    def active(self) -> ParticipantQuerySet:
        return self.filter(is_active=True)

    def inactive(self) -> ParticipantQuerySet:
        return self.filter(is_active=False)

    def active_for_race_grouped_by_race_type_and_ftt_count(
        self, race_id
    ) -> ParticipantQuerySet:

        return (
            self.for_race_id(race_id)
            .active()
            .values("race_type", "is_ftt")
            .annotate(count=Count("id"))
        )
