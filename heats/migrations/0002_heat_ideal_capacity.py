# Generated by Django 5.0 on 2024-01-31 20:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("heats", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="heat",
            name="ideal_capacity",
            field=models.IntegerField(default=0),
        ),
    ]
