from django.db import models


class CheckIn(models.Model):
    """
    A CheckIn location used to keep track of participants. Each Race Type can use different Check Ins.
    A Check In can depend on another Check In, that is, this Check In can not be completed before the other CheckIn is
    completed.
    """

    name = models.CharField(max_length=256)
    positive_action = models.CharField(max_length=256)
    negative_action = models.CharField(max_length=256)

    depends_on = models.ForeignKey(
        to="CheckIn",
        on_delete=models.CASCADE,
        related_name="dependents",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class CheckInUserBase(models.Model):
    """
    An abstract base class for any users that check in.
    """

    class Meta:
        abstract = True

    check_in = models.ForeignKey(
        CheckIn, on_delete=models.PROTECT, related_name="%(class)s_check_ins"
    )
    is_checked_in = models.BooleanField(default=False)
    date_changed = models.DateTimeField(auto_now=True)
