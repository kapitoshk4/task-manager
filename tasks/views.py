from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import ListView

from tasks import models
from tasks.forms import LoginForm
from tasks.models import Task, Project


@login_required
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


def logout_view(request):
    logout(request)
    return redirect("/login/")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "tasks/task_list.html"


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    context_object_name = "project_list"
    template_name = "tasks/project_list.html"


@login_required
def project_detail(request, pk):
    project = Project.objects.get(id=pk)

    context = {
        "project": project,
        "show_tabs": True
    }

    return render(request, "tasks/project_detail.html", context)
