from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from tasks.models import Project, Task


class WorkerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(
            username="Test3",
            password="test1234"
        )

    def test_worker_str(self):
        worker = get_user_model().objects.get(id=1)
        self.assertEqual(
            str(worker),
            f"{worker.username} ({worker.first_name} {worker.last_name})"
        )


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        worker = get_user_model().objects.create_user(
            username="Test3",
            password="test1234",
            first_name="Test1",
            last_name="Test2"
        )
        Project.objects.create(
            title="TestTitle",
            creator=worker
        )

    def test_project_str(self):
        project = Project.objects.get(id=1)
        self.assertEqual(str(project), "TestTitle - creator: Test3 (Test1 Test2)")

    def test_get_absolute_url(self):
        project = Project.objects.get(id=1)
        self.assertEqual(project.get_absolute_url(), "/projects/1/")


class TaskModelTest(TestCase):
    def setUp(self):
        worker = get_user_model().objects.create_user(
            username="Test3",
            password="test1234",
            first_name="Test1",
            last_name="Test2"
        )
        project = Project.objects.create(
            title="TestTitle",
            creator=worker
        )

        deadline = datetime.strptime("05/20/2024", "%m/%d/%Y").date()

        Task.objects.create(
            name="TestTask",
            project=project,
            creator=worker,
            deadline=deadline
        )

    def test_task_str(self):
        task = Task.objects.get(id=1)
        self.assertEqual(str(task), "TestTask 2024-05-20")

    def test_get_absolute_url(self):
        task = Task.objects.get(id=1)
        self.assertEqual(task.get_absolute_url(), "/projects/1/tasks/1/")
