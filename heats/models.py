from django.db import models


class Heat(models.Model):
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
        max_length=7, verbose_name="HEX Color Code", help_text="Color hex code with #"
    )

    def __str__(self):
        return "{} Heat Termination {}".format(
            self.start_datetime.strftime("%d/%m/%Y, %H:%M"), self.termination
        )
