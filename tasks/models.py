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
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)

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

    def __str__(self):
        return f"{self.name} {self.deadline}"


class Project(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField()
    creator = models.ForeignKey(Worker, on_delete=models.CASCADE)
    assignees = models.ManyToManyField(Worker, related_name="projects")


class Chat(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class ChatMessage(models.Model):
    message = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class TaskComment(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
