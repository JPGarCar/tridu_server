import datetime

from django.db import models


class ActiveModel(models.Model):
    """
    An abstract model that other models can extend to get Active/Inactive functionality.
    """

    is_active = models.BooleanField(default=True)
    date_active_changed = models.DateTimeField(
        editable=False, default=datetime.datetime.now
    )

    class Meta:
        abstract = True

    def activate(self) -> None:
        """
        Activate the instance, does not save the instance
        :return: None
        """
        self.is_active = True
        self.date_active_changed = datetime.datetime.now()

    def deactivate(self) -> None:
        """
        Deactivate the instance, does not save the instance
        :return: None
        """
        self.is_active = False
        self.date_active_changed = datetime.datetime.now()
