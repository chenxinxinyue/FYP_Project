# Generated by Django 5.0.3 on 2024-04-02 17:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("MainApp", "0005_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="detailedjob",
            name="max_salary",
        ),
        migrations.RemoveField(
            model_name="detailedjob",
            name="min_salary",
        ),
    ]
