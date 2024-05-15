# Generated by Django 4.2.11 on 2024-04-23 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0011_remove_project_chat_project_messages_delete_chat"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="messages",
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="project",
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="tasks.project"),
            preserve_default=False,
        ),
    ]
