from django.urls import path

from tasks.views import (
    index,
    task_list_view,
    UserLoginView,
    logout_view,
    UserRegistrationView,
    ProjectListView,
    project_detail,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    generate_code_view,
    join_project_view,
    chat_messages_view, TaskCreateView,
)

urlpatterns = [
    path("", index, name="index"),
    path("accounts/login/", UserLoginView.as_view(), name="login"),
    path("accounts/logout/", logout_view, name="logout"),
    path("accounts/register/", UserRegistrationView.as_view(), name="register"),
    path("projects/",
         ProjectListView.as_view(),
         name="project-list"
         ),
    path("projects/<int:pk>/",
         project_detail,
         name="project-detail"
         ),
    path("projects/<int:pk>/tasks/",
         task_list_view,
         name="task-list"),
    path("projects/<int:pk>/tasks/add",
         TaskCreateView.as_view(),
         name="task-add"),
    path("projects/create/",
         ProjectCreateView.as_view(),
         name="project-create"
         ),
    path("projects/<int:pk>/update",
         ProjectUpdateView.as_view(),
         name="project-update"
         ),
    path("projects/<int:pk>/delete",
         ProjectDeleteView.as_view(),
         name="project-delete"),
    path("projects/<int:pk>/invitation",
         generate_code_view,
         name="project-invitation"),
    path("projects/join",
         join_project_view,
         name="project-join"),
    path("projects/<int:pk>/chat",
         chat_messages_view,
         name="project-chat")
]

app_name = "tasks"
