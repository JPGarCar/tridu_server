# Generated by Django 5.0.1 on 2024-02-06 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "participants",
            "0004_alter_participant_bib_number_alter_participant_team_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="participant",
            name="location",
            field=models.CharField(default="", max_length=256),
        ),
    ]
