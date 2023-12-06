from django.db import models

from tridu_server.models import ActiveModel


class Race(ActiveModel):
    """
    The overarching model where we bin participants and heats.
    """

    name = models.CharField(max_length=255)


class RaceType(ActiveModel):
    """
    The types of races there are.
    """

    name = models.CharField(max_length=255)
