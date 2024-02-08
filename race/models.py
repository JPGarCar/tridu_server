import datetime

from django.db import models

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

    name = models.CharField(max_length=255)
    participants_allowed = models.PositiveIntegerField(default=0)
    ftt_allowed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
