# Generated by Django 5.0.1 on 2024-02-08 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("race", "0002_race_date_active_changed_race_date_created_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="racetype",
            name="ftt_allowed",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="racetype",
            name="participants_allowed",
            field=models.PositiveIntegerField(default=0),
        ),
    ]