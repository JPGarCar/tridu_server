from django.db import models

from checkins.models import CheckIn
from race.querysets import RaceTypeQuerySet
from tridu_server.models import ActiveModel


class Race(ActiveModel):
    """
    The overarching model where we bin participants and heats.
    """

    name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RaceType(ActiveModel):
    """
    The types of races there are.
    """

    objects = RaceTypeQuerySet.as_manager()

    name = models.CharField(max_length=255)
    participants_allowed = models.PositiveIntegerField(default=0)
    ftt_allowed = models.PositiveIntegerField(default=0)
    needs_swim_time = models.BooleanField(default=True)

    checkins = models.ManyToManyField(
        to=CheckIn, blank=True, null=True, related_name="used_by_race_types"
    )

    def __str__(self):
        return self.name
