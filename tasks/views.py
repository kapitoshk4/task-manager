import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Q

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic, View
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


class IndexView(generic.View):
    template_name = "tasks/index.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_projects = Project.objects.filter(
                Q(creator=request.user) | Q(assignees=request.user)
            ).distinct()

            project_ids = set(user_projects.values_list('id', flat=True))
            num_projects = len(project_ids)
            num_tasks = Task.objects.filter(creator=request.user).count()

            context = {
                "num_projects": num_projects,
                "num_tasks": num_tasks
            }

            return render(request, self.template_name, context)

        return render(request, self.template_name)


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm


class LogoutView(View):
    @staticmethod
    def get(request, *args, **kwargs):
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


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "task_list"

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs["pk"])
        queryset = super().get_queryset().filter(project=project, creator=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, id=self.kwargs["pk"])
        context["project"] = project
        context["show_tabs"] = True

        return context


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

        return HttpResponseForbidden("You do not have permission to view this page.")


class TaskDetailView(LoginRequiredMixin, generic.View):
    @staticmethod
    def get(request, pk, task_pk):
        project = get_object_or_404(Project, pk=pk)
        task = get_object_or_404(Task, id=task_pk)
        comments = TaskComment.objects.filter(task=task)
        if request.user not in project.assignees.all():
            return HttpResponseForbidden("You do not have permission to this page.")
        form = CommentForm()
        context = {
            "form": form,
            "task": task,
            "project": project,
            "show_tabs": True,
            "comments": comments
        }

        return render(request, "tasks/task_detail.html", context)

    @staticmethod
    def post(request, pk, task_pk):
        project = get_object_or_404(Project, pk=pk)
        task = get_object_or_404(Task, id=task_pk)
        comments = TaskComment.objects.filter(task=task)
        if request.user not in project.assignees.all():
            return HttpResponseForbidden("You do not have permission to this page.")
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


class TaskUpdateView(LoginRequiredMixin, generic.View):
    @staticmethod
    def get(request, pk, task_pk):
        project = get_object_or_404(Project, pk=pk)
        task = get_object_or_404(Task, id=task_pk)

        if request.user != task.creator:
            return HttpResponseForbidden("You do not have permission to this page.")

        form = TaskForm(instance=task)

        context = {
            "form": form,
            "project": project,
            "task": task,
            "show_tabs": True
        }

        return render(request, "tasks/task_form.html", context)

    @staticmethod
    def post(request, pk, task_pk):
        project = get_object_or_404(Project, pk=pk)
        task = get_object_or_404(Task, id=task_pk)

        if request.user != task.creator:
            return HttpResponseForbidden("You do not have permission to this page.")

        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.instance.creator_id = request.user.id
            form.instance.project_id = pk
            form.save()

            return redirect("tasks:task-list", pk=pk)

        context = {
            "form": form,
            "project": project,
            "task": task,
            "show_tabs": True
        }

        return render(request, "tasks/task_form.html", context)


class TaskDeleteView(LoginRequiredMixin, generic.View):
    @staticmethod
    def post(request, pk, task_pk):
        task = get_object_or_404(Task, id=task_pk)

        if request.user != task.creator:
            return HttpResponseForbidden("You do not have permission to this page.")

        task.delete()

        return redirect("tasks:task-list", pk=pk)

    @staticmethod
    def get(request, pk, task_pk):
        project = get_object_or_404(Project, pk=pk)
        task = get_object_or_404(Task, id=task_pk)

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


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = "tasks/project_detail.html"
    context_object_name = "project"

    def dispatch(self, request, *args, **kwargs):
        if request.user == self.get_object().creator or request.user in self.get_object().assignees.all():
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden("You do not have permission to this page")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["show_tabs"] = True
        context["project"] = self.object

        return context


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


class GenerateCodeView(LoginRequiredMixin, generic.View):
    @staticmethod
    def get(request, pk):
        project = get_object_or_404(Project, id=pk)
        if request.user != project.creator:
            return HttpResponseForbidden("You do not have permission to this project.")

        project.invitation_code = uuid.uuid4()
        project.save()
        context = {
            "project": project
        }

        return render(request, "tasks/project_invitation.html", context)


class JoinProjectView(LoginRequiredMixin, generic.View):
    @staticmethod
    def get(request):
        form = JoinProjectForm()

        return render(request, "tasks/project_join_form.html", {"form": form})

    @staticmethod
    def post(request):
        form = JoinProjectForm(request.POST)
        if form.is_valid():
            invitation_code = form.cleaned_data.get("invitation_code")
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


class ChatMessagesView(LoginRequiredMixin, generic.View):
    @staticmethod
    def get(request, pk):
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

        return HttpResponseForbidden("You do not have permission to view this project.")

    @staticmethod
    def post(request, pk):
        project = get_object_or_404(Project, id=pk)

        if request.user == project.creator or request.user in project.assignees.all():
            message_form = ChatMessageForm(request.POST)
            if message_form.is_valid():
                new_message = message_form.save(commit=False)
                new_message.project = project
                new_message.sender = request.user
                new_message.save()

                return redirect("tasks:project-chat", pk=pk)
            else:
                messages_connected = ChatMessage.objects.filter(project=project)
                context = {
                    "project": project,
                    "messages": messages_connected,
                    "message_form": message_form,
                    "show_tabs": True
                }

                return render(request, "tasks/chat_messages.html", context)

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
        new_profile_image = self.request.FILES.get("profile_image")
        if new_profile_image:
            profile.profile_image = new_profile_image

        profile.save()

        return super().form_valid(form)
