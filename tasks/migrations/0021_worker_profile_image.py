# Generated by Django 4.2.11 on 2024-05-13 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0020_alter_taskcomment_options_task_modified"),
    ]

    operations = [
        migrations.AddField(
            model_name="worker",
            name="profile_image",
            field=models.ImageField(blank=True, upload_to="user/%Y/%m/%d/"),
        ),
    ]