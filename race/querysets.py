from __future__ import annotations

from django.db.models import QuerySet, Q


class RaceTypeQuerySet(QuerySet):

    def for_race(self, race_id) -> "RaceTypeQuerySet":
        return self.filter(
            Q(participants__race_id=race_id) | Q(relay_teams__race_id=race_id)
        )
