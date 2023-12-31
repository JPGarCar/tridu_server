# Generated by Django 5.0 on 2023-12-06 22:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("race", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Heat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("termination", models.CharField(max_length=10)),
                ("start_datetime", models.DateTimeField()),
                (
                    "color",
                    models.CharField(
                        help_text="Color hex code with #",
                        max_length=7,
                        verbose_name="HEX Color Code",
                    ),
                ),
                (
                    "race",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="heats",
                        to="race.race",
                    ),
                ),
                (
                    "race_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="heats",
                        to="race.racetype",
                    ),
                ),
            ],
        ),
    ]
