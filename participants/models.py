from django.db import models

from tridu_server import settings


class Participant(models.Model):
    """
    A participant will be part of the race. It holds participant only information,
    any other personal information can be found in the user model
    """

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    bib_number = models.IntegerField(db_index=True, unique=True)
    is_ftt = models.BooleanField(default=False, verbose_name="Is First Time Triathlete")
    team = models.CharField(max_length=255, verbose_name="Team Name")
    swim_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return self.user.__str__()
