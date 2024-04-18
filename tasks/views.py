from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.shortcuts import render
from django.views import generic
from django.views.generic import ListView

from tasks import models
from tasks.forms import LoginForm
from tasks.models import Task, Project


def index(request):
    num_projects = Project.objects.count()
    num_tasks = Task.objects.count()
    context = {
        "num_projects": num_projects,
        "num_tasks": num_tasks
    }

    return render(request, "tasks/index.html", context)


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "tasks/task_list.html"


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    context_object_name = "project_list"
    template_name = "tasks/project_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(num_assignees=Count("assignees"))
        return queryset
