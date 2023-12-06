from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Genders(models.TextChoices):
        """
        Choices for the gender field
        """

        MALE = "M"
        FEMALE = "F"
        NON_BINARY = "NB"
        UNDEFINED = "U"

    phone_number = models.CharField(max_length=20, null=True, blank=True)

    gender = models.CharField(
        max_length=12,
        choices=Genders,
        default=Genders.UNDEFINED,
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.username
