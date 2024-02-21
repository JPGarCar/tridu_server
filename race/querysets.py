from __future__ import annotations

from django.db.models import QuerySet


class RaceTypeQuerySet(QuerySet):

    def for_race(self, race_id) -> "RaceTypeQuerySet":
        return self.filter(participants__race_id=race_id)
