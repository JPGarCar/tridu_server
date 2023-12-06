from django.db import models


class ActiveModel(models.Model):
    """
    An abstract model that other models can extend to get Active/Inactive functionality.
    """

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
