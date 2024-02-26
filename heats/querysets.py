from __future__ import annotations

from django.db import models


class HeatQuerySet(models.QuerySet):

    def for_race(self, race_id: int) -> HeatQuerySet:
        return self.filter(race_id=race_id)

    def for_race_type(self, race_type_id: int) -> HeatQuerySet:
        return self.filter(race_type_id=race_type_id)
