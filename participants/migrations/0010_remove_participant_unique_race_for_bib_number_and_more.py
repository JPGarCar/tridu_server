# Generated by Django 5.0.1 on 2024-02-09 23:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("heats", "0003_heat_pool"),
        ("locations", "0001_initial"),
        ("participants", "0009_alter_participant_location"),
        ("race", "0003_racetype_ftt_allowed_racetype_participants_allowed"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="participant",
            name="unique_race_for_bib_number",
        ),
        migrations.AddConstraint(
            model_name="participant",
            constraint=models.UniqueConstraint(
                fields=("bib_number", "race"),
                name="unique_race_for_bib_number",
                violation_error_message="Participant must have a unique BibNumber in this Race.",
            ),
        ),
    ]