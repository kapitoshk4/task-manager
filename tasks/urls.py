from django.urls import path

from tasks.views import index, TaskListView, UserLoginView

urlpatterns = [
    path("", index, name="index"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("tasks/",
         TaskListView.as_view(),
         name="task-list"
         )
]
