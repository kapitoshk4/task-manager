from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task


class Command(BaseCommand):
    help = "Delete tasks based on their deadline and status"

    def handle(self, *args, **kwargs):
        tasks = Task.objects.all()

        today = timezone.now().date()

        for task in tasks:
            if task.status == "Done" and (today - task.modified.date()).days >= 1:
                task.delete()
            elif task.deadline and (today - task.deadline).days >= 1:
                task.delete()
