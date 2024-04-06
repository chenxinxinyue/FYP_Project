# Generated by Django 5.0.3 on 2024-04-06 17:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MainApp", "0012_alter_experience_job_duration"),
    ]

    operations = [
        migrations.CreateModel(
            name="School",
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
                ("country", models.CharField(max_length=100)),
                ("name", models.CharField(max_length=100)),
                ("website", models.URLField()),
            ],
        ),
    ]