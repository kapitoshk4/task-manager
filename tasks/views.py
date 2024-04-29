import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseForbidden

from tasks.forms import (
    RegistrationForm,
    LoginForm,
    ProjectForm,
    JoinProjectForm,
    ChatMessageForm,
    ProjectSearchForm
)
from tasks.models import Task, Project, ChatMessage


def index(request):
    if request.user.is_authenticated:
        num_projects = (
                Project.objects.filter(creator=request.user).count() +
                Project.objects.filter(assignees=request.user).distinct().count()
        )
        num_tasks = Task.objects.count()
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


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "tasks/task_list.html"


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


class ChatMessagesView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = "tasks/chat_messages.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        messages_connected = ChatMessage.objects.filter(
            project=self.get_object()
        )
        data["messages"] = messages_connected

        if self.request.user.is_authenticated:
            data["message_form"] = ChatMessageForm()

        data["show_tabs"] = True

        return data

    def post(self, request, *args, **kwargs):
        project_object = self.get_object()
        new_message = ChatMessage(message=request.POST.get("message"),
                                  sender=self.request.user,
                                  project=project_object)
        new_message.save()
        return redirect("tasks:project-chat", pk=project_object.pk)
