from django.db import models


class Location(models.Model):
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        unique_together = [["city", "province", "country"]]
        index_together = [["city", "province", "country"]]
