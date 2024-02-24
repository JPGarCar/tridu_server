from django.db import models
from django.db.models import Q

from comments.models import Comment
from participants.querysets import ParticipantQuerySet, RelayParticipantQuerySet
from tridu_server import settings
from tridu_server.models import ActiveModel


class BaseParticipant(ActiveModel):
    """
    A base class for all participants. It connects to the User model, Location (origin) Model and Wetbags on Firebase.
    """

    class Meta:
        abstract = True

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s"
    )

    origin = models.ForeignKey(
        to="locations.Location",
        on_delete=models.PROTECT,
        related_name="%(class)s",
        null=True,
        blank=True,
    )

    date_changed = models.DateTimeField(auto_now=True)
    location = models.CharField(
        max_length=256, default="", db_default="", null=True, blank=True
    )

    def __str__(self):
        return self.user.__str__()


class Participant(BaseParticipant):
    """
    A participant will be part of the race. It holds participant only information,
    any other personal information can be found in the user model
    """

    objects = ParticipantQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "race"],
                name="unique_participant_per_race_and_user",
                violation_error_message="This user is already registered for this race!",
            ),
            models.UniqueConstraint(
                fields=["bib_number", "race"],
                condition=Q(is_active=True),
                name="unique_race_for_participant_bib_number",
                violation_error_message="Another active participant is already using this bib number.",
            ),
        ]

    heat = models.ForeignKey(
        to="heats.Heat",
        on_delete=models.SET_NULL,
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

    bib_number = models.IntegerField(db_index=True)
    is_ftt = models.BooleanField(default=False, verbose_name="Is First Time Triathlete")
    team = models.CharField(
        max_length=255, verbose_name="Team Name", null=True, blank=True
    )
    swim_time = models.DurationField(null=True, blank=True)


class RelayParticipant(BaseParticipant):
    """
    A relay participant is part of a relay team in a race.
    """

    objects = RelayParticipantQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"],
                name="unique_relay_participant_for_user_and_team",
                violation_error_message="This user is already registered for this team!",
            )
        ]

    team = models.ForeignKey(
        to="RelayTeam", on_delete=models.PROTECT, related_name="participants"
    )


class RelayTeam(ActiveModel):
    """
    A relay team is composed of multiple RelayParticipants. They participate together in a race.
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "race"],
                name="unique_race_for_relay_team_name",
                violation_error_message="This team name is already registered for this race!",
            ),
            models.UniqueConstraint(
                fields=["bib_number", "race"],
                condition=Q(is_active=True),
                name="unique_race_for_relay_team_bib_number",
                violation_error_message="Another active relay team is already using this bib number.",
            ),
        ]

    heat = models.ForeignKey(
        to="heats.Heat",
        on_delete=models.SET_NULL,
        related_name="relay_teams",
        null=True,
        blank=True,
    )

    race = models.ForeignKey(
        to="race.Race", on_delete=models.PROTECT, related_name="relay_teams"
    )

    race_type = models.ForeignKey(
        to="race.RaceType", on_delete=models.PROTECT, related_name="relay_teams"
    )

    bib_number = models.IntegerField(db_index=True)
    name = models.CharField(max_length=255, verbose_name="Relay Team Name")


class ParticipantComment(Comment):
    """
    A comment in a Participant object.
    """

    participant = models.ForeignKey(
        to=Participant, on_delete=models.CASCADE, related_name="comments"
    )


class RelayTeamComment(Comment):
    """
    A comment in a relay team object.
    """

    relay_team = models.ForeignKey(
        to="RelayTeam", on_delete=models.CASCADE, related_name="comments"
    )
