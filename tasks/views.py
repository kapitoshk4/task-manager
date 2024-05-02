import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseForbidden, HttpResponseNotFound

from tasks.forms import (
    RegistrationForm,
    LoginForm,
    ProjectForm,
    JoinProjectForm,
    ChatMessageForm,
    ProjectSearchForm, TaskForm
)
from tasks.models import Task, Project, ChatMessage


def index(request):
    if request.user.is_authenticated:
        num_projects = (
                Project.objects.filter(creator=request.user).count() +
                Project.objects.filter(assignees=request.user).distinct().count()
        )
        num_tasks = Task.objects.filter(creator=request.user).count()
        context = {
            "num_projects": num_projects,
            "num_tasks": num_tasks
        }
        return render(request, "tasks/index.html", context)
    return render(request, "tasks/index.html")


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm


def logout_view(request):
    logout(request)
    return redirect("/")


class UserRegistrationView(generic.CreateView):
    template_name = "accounts/signup.html"
    form_class = RegistrationForm
    success_url = "/login/"


@login_required
def task_list_view(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.user == project.creator or request.user in project.assignees.all():
        tasks = Task.objects.filter(project=project)
        context = {
            "project": project,
            "task_list": tasks,
            "show_tabs": True
        }
        return render(request, "tasks/task_list.html", context)
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")


@login_required
def task_detail_view(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, id=task_pk)

    if request.user == project.creator or request.user in project.assignees.all():
        context = {
            "task": task,
            "project": project,
            "show_tabs": True
        }

        return render(request, "tasks/task_detail.html", context)
    return HttpResponseForbidden("You do not have permission to this page.")


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        form.instance.creator_id = self.request.user.id
        form.instance.project_id = self.kwargs['pk']
        return super().form_valid(form)


def task_update_view(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, id=task_pk)

    if request.user != project.creator and request.user not in project.assignees.all():
        return HttpResponseForbidden("You do not have permission to this page.")

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.instance.creator_id = request.user.id
            form.instance.project_id = pk
            form.save()
            return redirect('tasks:task-list', pk=pk)
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'project': project,
        'task': task,
        'show_tabs': True
    }

    return render(request, 'tasks/task_form.html', context)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    queryset = Project.objects.all()
    context_object_name = "project_list"
    template_name = "tasks/project_list.html"
    paginate_by = 3

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(creator=user) | self.queryset.filter(assignees=user)

        form = ProjectSearchForm(self.request.GET)  # Bind form to GET data
        if form.is_valid():
            title = form.cleaned_data.get("title")
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        context["search_form"] = ProjectSearchForm(
            initial={"title": title}
        )
        context["show_search"] = True

        return context


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.user == project.creator or request.user in project.assignees.all():
        context = {
            "project": project,
            "show_tabs": True
        }

        return render(request, "tasks/project_detail.html", context)
    return HttpResponseForbidden("You do not have permission to this project.")


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    template_name = "tasks/project_form.html"
    form_class = ProjectForm
    success_url = reverse_lazy("tasks:project-list")

    def form_valid(self, form):
        form.instance.creator_id = self.request.user.id
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy("tasks:project-list")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().creator != self.request.user:
            return HttpResponseForbidden("You do not have permission to this project.")
        return super().dispatch(request, *args, **kwargs)


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    success_url = reverse_lazy("tasks:project-list")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().creator != self.request.user:
            return HttpResponseForbidden("You do not have permission to this project.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def generate_code_view(request, pk):
    project = get_object_or_404(Project, id=pk)
    if request.user != project.creator:
        return HttpResponseForbidden("You do not have permission to this project.")

    project.invitation_code = uuid.uuid4()
    project.save()
    context = {
        "project": project
    }
    return render(request, "tasks/project_invitation.html", context)


@login_required
def join_project_view(request):
    form = JoinProjectForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            invitation_code = request.POST.get("invitation_code")
            try:
                project = Project.objects.get(invitation_code=invitation_code)
            except Project.DoesNotExist:
                messages.warning(request, "Invalid invitation code.")
                return redirect("tasks:project-join")
            if project.assignees.filter(id=request.user.id).exists():
                messages.warning(request, "You are already a member of this project.")
                return redirect("tasks:project-join")
            project.assignees.add(request.user)
            return redirect(project.get_absolute_url())
        else:
            error_message = form.errors.get("invitation_code")
            if error_message:
                messages.warning(request, error_message)
    return render(request, "tasks/project_join_form.html", {"form": form})


@login_required
def chat_messages_view(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.user == project.creator or request.user in project.assignees.all():
        messages_connected = ChatMessage.objects.filter(project=project)
        context = {
            "project": project,
            "messages": messages_connected,
            "message_form": ChatMessageForm(),
            "show_tabs": True
        }
        return render(request, "tasks/chat_messages.html", context)
    else:
        return HttpResponseForbidden("You do not have permission to view this project.")
