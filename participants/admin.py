from django.contrib import admin

from participants.models import Participant, ParticipantComment


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(ParticipantComment)
class ParticipantCommentAdmin(admin.ModelAdmin):
    pass
