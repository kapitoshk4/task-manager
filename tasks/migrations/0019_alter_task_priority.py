# Generated by Django 4.2.11 on 2024-05-11 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0018_alter_taskcomment_task"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="priority",
            field=models.CharField(choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")], default="Medium", max_length=10),
        ),
    ]
