from django.contrib import admin

from participants.models import (
    Participant,
    ParticipantComment,
    RelayParticipant,
    RelayTeam,
)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(ParticipantComment)
class ParticipantCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(RelayParticipant)
class RelayParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(RelayTeam)
class RelayTeamAdmin(admin.ModelAdmin):
    pass
