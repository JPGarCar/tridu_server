from django.contrib import admin

from race.models import Race, RaceType


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    pass


@admin.register(RaceType)
class RaceTypeAdmin(admin.ModelAdmin):
    pass
