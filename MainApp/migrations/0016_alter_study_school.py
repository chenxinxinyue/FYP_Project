# Generated by Django 5.0.3 on 2024-04-06 17:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MainApp", "0015_alter_school_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="study",
            name="school",
            field=models.CharField(max_length=255),
        ),
    ]