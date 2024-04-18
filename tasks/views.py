from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic
from django.views.generic import ListView

from tasks.models import Task, Project


def index(request):
    projects = Project.objects.all()
    context = {
        "projects": projects
    }

    return render(request, "tasks/index.html", context)


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "tasks/task_list.html"
