from django.test import TestCase
from django.utils import timezone
from tasks.models import Task
from django.core.management import call_command


class DeleteTasksTestCase(TestCase):
    def setUp(self):
        self.task1 = Task.objects.create(
            name="Task 1",
            status="Done",
            deadline=timezone.now() - timezone.timedelta(days=2)
        )

        self.task2 = Task.objects.create(
            name="Task 2",
            status="To do",
            deadline=timezone.now() - timezone.timedelta(days=2)
        )

        self.task3 = Task.objects.create(
            name="Task 3",
            status="To do",
            deadline=timezone.now()
        )

    def test_task_deletion(self):
        call_command("delete_tasks")

        self.assertFalse(Task.objects.filter(pk=self.task1.pk).exists(), msg="Task 1 should be deleted")
        self.assertFalse(Task.objects.filter(pk=self.task2.pk).exists(), msg="Task 2 should be deleted")
        self.assertTrue(Task.objects.filter(pk=self.task3.pk).exists(), msg="Task 3 should not be deleted")
