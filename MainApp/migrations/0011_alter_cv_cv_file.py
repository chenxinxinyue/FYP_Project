# Generated by Django 5.0.3 on 2024-04-05 21:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MainApp", "0010_rename_job_description_experience_job_detail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cv",
            name="cv_file",
            field=models.FileField(upload_to="MainApp/cvs/"),
        ),
    ]