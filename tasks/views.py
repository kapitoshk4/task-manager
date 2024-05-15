import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Q

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseForbidden

from tasks.forms import (
    RegistrationForm,
    LoginForm,
    ProjectForm,
    UserPasswordChangeForm,
    JoinProjectForm,
    ChatMessageForm,
    ProjectSearchForm,
    TaskForm,
    CommentForm,
    ProjectTaskSearchForm,
    ProfileForm
)
from tasks.models import (
    Task,
    Project,
    ChatMessage,
    TaskComment,
    Worker
)


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
    template_name = "accounts/login.html"
    form_class = LoginForm


def logout_view(request):
    logout(request)
    return redirect("/")


class UserRegistrationView(generic.CreateView):
    template_name = "accounts/signup.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("tasks:login")


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("tasks:login")
    template_name = "accounts/change_password.html"


@login_required
def task_list_view(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.user == project.creator or request.user in project.assignees.all():
        user_tasks = Task.objects.filter(project=project, creator=request.user)
        context = {
            "project": project,
            "task_list": user_tasks,
            "show_tabs": True
        }
        return render(request, "tasks/task_list.html", context)
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")


class ProjectTaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "tasks/project_task_list.html"
    context_object_name = "project_tasks"
    paginate_by = 10

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs["pk"])
        queryset = super().get_queryset().filter(project=project)
        search_query = self.request.GET.get("title", None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, id=self.kwargs["pk"])
        context["project"] = project
        context["search_form"] = ProjectTaskSearchForm()
        context["show_tabs"] = True
        context["show_search"] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=self.kwargs["pk"])
        if request.user in project.assignees.all() or request.user == project.creator:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to view this page.")


@login_required
def task_detail_view(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, id=task_pk)
    comments = TaskComment.objects.filter(task=task)
    if request.user not in project.assignees.all():
        return HttpResponseForbidden("You do not have permission to this page.")

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.sender = request.user
            comment.task = task
            comment.save()
    else:
        form = CommentForm()

    context = {
        "form": form,
        "task": task,
        "project": project,
        "show_tabs": True,
        "comments": comments
    }

    return render(request, "tasks/task_detail.html", context)


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        form.instance.creator_id = self.request.user.id
        form.instance.project_id = self.kwargs["pk"]
        self.success_url = reverse_lazy("tasks:task-list", kwargs={"pk": self.kwargs["pk"]})
        return super().form_valid(form)


@login_required
def task_update_view(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, id=task_pk)

    if request.user != task.creator:
        return HttpResponseForbidden("You do not have permission to this page.")

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.instance.creator_id = request.user.id
            form.instance.project_id = pk
            form.save()
            return redirect("tasks:task-list", pk=pk)
    else:
        form = TaskForm(instance=task)

    context = {
        "form": form,
        "project": project,
        "task": task,
        "show_tabs": True
    }

    return render(request, "tasks/task_form.html", context)


@login_required
def task_delete_view(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(Task, id=task_pk)

    if request.user != task.creator:
        return HttpResponseForbidden("You do not have permission to this page.")

    if request.method == "POST":
        task.delete()
        return redirect("tasks:task-list", pk=pk)

    context = {
        "project": project,
        "task": task,
        "show_tabs": True
    }

    return render(request, "tasks/task_confirm_delete.html", context)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    queryset = Project.objects.all()
    context_object_name = "project_list"
    template_name = "tasks/project_list.html"
    paginate_by = 3

    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.filter(Q(creator=user) | Q(assignees=user)).distinct()

        form = ProjectSearchForm(self.request.GET)
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
        project = form.save(commit=False)
        project.creator = self.request.user
        project.save()
        project.assignees.add(self.request.user)

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
        if request.method == "POST":
            message_form = ChatMessageForm(request.POST)
            if message_form.is_valid():
                new_message = message_form.save(commit=False)
                new_message.project = project
                new_message.sender = request.user
                new_message.save()
                return redirect("tasks:project-chat", pk=pk)

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


class ProfileDetailView(LoginRequiredMixin, generic.DetailView):
    worker = Worker
    success_url = reverse_lazy("tasks:profile-detail")
    template_name = "tasks/profile_detail.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    worker = Worker
    success_url = reverse_lazy("tasks:profile-detail")
    template_name = "tasks/profile_form.html"
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.profile_image = self.request.FILES.get("profile_image")
        profile.save()

        return super().form_valid(form)
