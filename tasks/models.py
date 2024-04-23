import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from task_manager import settings


class Position(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class Task(models.Model):
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"

    PRIORITY_CHOICES = [
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    ]

    TODO = "TD"
    DOING = "DG"
    DONE = "DE"

    STATUS_CHOICES = [
        (TODO, "To do"),
        (DOING, "Doing"),
        (DONE, "Done"),
    ]

    name = models.CharField(max_length=63)
    description = models.TextField()
    deadline = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=TODO)
    task_type = models.ForeignKey(TaskType,
                                  related_name="tasks",
                                  on_delete=models.SET_NULL,
                                  null=True)

    def __str__(self):
        return f"{self.name} {self.deadline}"


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    tasks = models.ManyToManyField(Task, related_name="workers")

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Project(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="projects")
    invitation_code = models.UUIDField(editable=False, unique=True, null=True, blank=True)

    class Meta:
        ordering = ("name", )

    def get_absolute_url(self):
        return reverse("tasks:project-detail", kwargs={"pk": self.pk})


class ChatMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class TaskComment(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
