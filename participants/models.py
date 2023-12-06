from django.db import models

from comments.models import Comment
from tridu_server import settings


class Participant(models.Model):
    """
    A participant will be part of the race. It holds participant only information,
    any other personal information can be found in the user model
    """

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    origin = models.ForeignKey(
        to="locations.Location",
        on_delete=models.PROTECT,
        related_name="participants",
        null=True,
        blank=True,
    )

    heat = models.ForeignKey(
        to="heats.Heat",
        on_delete=models.PROTECT,
        related_name="participants",
        null=True,
        blank=True,
    )

    race = models.ForeignKey(
        to="race.Race", on_delete=models.PROTECT, related_name="participants"
    )

    race_type = models.ForeignKey(
        to="race.RaceType", on_delete=models.PROTECT, related_name="participants"
    )

    bib_number = models.IntegerField(db_index=True, unique=True)
    is_ftt = models.BooleanField(default=False, verbose_name="Is First Time Triathlete")
    team = models.CharField(max_length=255, verbose_name="Team Name")
    swim_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return self.user.__str__()


class ParticipantComment(Comment):
    """
    A comment in a Participant object.
    """

    participant = models.ForeignKey(
        to=Participant, on_delete=models.CASCADE, related_name="comments"
    )
