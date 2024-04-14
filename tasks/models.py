from django.contrib.auth.models import AbstractUser
from django.db import models


class Position(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Task(models.Model):
    class Priority(models.TextChoices):
        H = "High"
        M = "Medium"
        L = "Low"

    class Status(models.TextChoices):
        todo = "To do"
        doing = "Doing"
        done = "Done"

    name = models.CharField(max_length=63)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10,
                                choices=Priority,
                                default=Priority.M
                                )
    status = models.CharField(max_length=10,
                              choices=Status,
                              default=Status.todo
                              )
    task_type = models.ForeignKey(TaskType,
                                  related_name="tasks",
                                  on_delete=models.SET("")
                                  )
    assignees = models.ManyToManyField(Worker, related_name='tasks')

    def __str__(self):
        return f"{self.name} {self.deadline}"
