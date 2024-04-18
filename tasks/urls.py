from django.urls import path

from tasks.views import (
    index,
    TaskListView,
    UserLoginView,
    logout_view,
    ProjectListView,
    project_detail
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
]
