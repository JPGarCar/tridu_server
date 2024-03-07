from django.db import models

from heats.querysets import HeatQuerySet


class Heat(models.Model):

    class Pools(models.TextChoices):
        """
        Choices for the pool field
        """

        RECREATION = "Recreation"
        COMPETITIVE = "Competitive"

    objects = HeatQuerySet.as_manager()

    race = models.ForeignKey(
        to="race.Race", on_delete=models.PROTECT, related_name="heats"
    )

    race_type = models.ForeignKey(
        to="race.RaceType",
        on_delete=models.PROTECT,
        related_name="heats",
    )

    termination = models.CharField(max_length=10)
    start_datetime = models.DateTimeField()
    color = models.CharField(
        max_length=10,
        verbose_name="HEX Color Code",
        help_text="Color hex code with 0x including opacity.",
    )
    ideal_capacity = models.IntegerField(default=0)
    pool = models.CharField(
        max_length=25, choices=Pools, default=Pools.RECREATION, null=True, blank=True
    )

    def __str__(self):
        return "{} Heat Termination {}".format(
            self.start_datetime.astimezone().strftime("%I:%M %p"), self.termination
        )
