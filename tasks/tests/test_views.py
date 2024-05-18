from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from tasks.models import Project, Task


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        self.project = Project.objects.create(title="Test Project", creator=self.user)
        self.task = Task.objects.create(name="Test Task", project=self.project, creator=self.user)

    def test_index_view_authenticated(self):
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/index.html")

    def test_index_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/index.html")

    def test_project_task_list_view(self):
        response = self.client.get(reverse("tasks:project-task-list", kwargs={"pk": self.project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/project_task_list.html")
        self.assertEqual(len(response.context["project_tasks"]), 1)
