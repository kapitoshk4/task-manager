from django.urls import path

from tasks.views import index, TaskListView

urlpatterns = [
    path("", index, name="index"),
    path("tasks/",
         TaskListView.as_view(),
         name="task-list"
         )
]
