# Generated by Django 4.2.11 on 2024-04-23 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0012_remove_project_messages_chatmessage_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="invitation_code",
            field=models.UUIDField(blank=True, editable=False, null=True, unique=True),
        ),
    ]
