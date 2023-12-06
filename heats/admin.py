from django.contrib import admin

from heats.models import Heat


@admin.register(Heat)
class HeatAdmin(admin.ModelAdmin):
    pass
