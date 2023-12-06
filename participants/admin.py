from django.contrib import admin

from participants.models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass
