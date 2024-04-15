from django.urls import path

from tasks.views import TaskListView

urlpatterns = [
    path("tasks/",
         TaskListView.as_view(),
         name="task-list"
         )
]
