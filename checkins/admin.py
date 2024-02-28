from django.contrib import admin

from checkins.models import CheckIn


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    pass
