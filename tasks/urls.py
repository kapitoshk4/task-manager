from django.urls import path

from tasks.views import (
    index,
    TaskListView,
    UserLoginView,
    logout_view,
    ProjectListView,
    project_detail,
    ProjectCreateView,
    ProjectUpdateView
)

urlpatterns = [
    path("", index, name="index"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("tasks/",
         TaskListView.as_view(),
         name="task-list"
         ),
    path("projects/",
         ProjectListView.as_view(),
         name="project-list"
         ),
    path("projects/<int:pk>/",
         project_detail,
         name="project-detail"
         ),
    path("projects/create/",
         ProjectCreateView.as_view(),
         name="project-create"
         ),
    path("projects/<int:pk>/update",
         ProjectUpdateView.as_view(),
         name="project-update"
         ),
]

app_name = "tasks"
