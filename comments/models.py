from django.db import models

from tridu_server import settings


class Comment(models.Model):
    comment = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    writer = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_comments",
        null=True,
        blank=True,
    )

    @property
    def is_system(self):
        return self.writer is None

    class Meta:
        abstract = True
        ordering = ("-creation_date",)

    def __str__(self):
        return "Comment by {}.".format(self.writer.__str__())
