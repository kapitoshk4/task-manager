from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from tasks.forms import (
    RegistrationForm,
    LoginForm,
    UserPasswordChangeForm,
    ProjectForm,
    JoinProjectForm,
    ChatMessageForm,
    ProjectSearchForm,
    TaskForm,
    CommentForm,
    ProjectTaskSearchForm,
    ProfileForm
)
from tasks.models import Position, TaskType


class RegistrationFormTest(TestCase):
    def setUp(self):
        self.deadline = datetime.strptime("05/20/2024", "%m/%d/%Y").date()
        self.priority = "Medium"
        self.status = "To do"
        self.task_type = TaskType.objects.create(name="Task Type")
        self.position = Position.objects.create(name="Test Position")
        self.test_user = get_user_model().objects.create_user(
            username="test_user",
            password="test_password"
        )

    def test_registration_form(self):
        form = RegistrationForm(
            data={
                "username": "username1",
                "email": "email@email.email",
                "password1": "test_password123",
                "password2": "test_password123",
                "first_name": "first_name1",
                "last_name": "last_name1",
                "position": self.position.id
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_login_form(self):
        form = LoginForm(
            data={
                "username": "test_user",
                "password": "test_password"
            }
        )
        self.assertTrue(form.is_valid())

    def test_user_password_change_form(self):
        form = UserPasswordChangeForm(
            user=self.test_user,
            data={
                "old_password": "test_password",
                "new_password1": "test_password123",
                "new_password2": "test_password123"
            }
        )
        self.assertTrue(form.is_valid())

    def test_project_form(self):
        form = ProjectForm(
            data={
                "title": "title1",
                "description": "description1",
                "creator": self.test_user,
                "assignees": self.test_user,
                "invitation_code": "TEST"
            }
        )

        self.assertTrue(form.is_valid())

    def test_join_project_form(self):
        form = JoinProjectForm(
            data={
                "invitation_code": "ec93f927-0ffb-4e76-9402-f83caf7c4c10"
            }
        )

        self.assertTrue(form.is_valid())

    def test_chat_message_form(self):
        form = ChatMessageForm(
            data={
                "message": "test message"
            }
        )

        self.assertTrue(form.is_valid())

    def test_project_search_form(self):
        form = ProjectSearchForm(
            data={
                "project_title": "Project1"
            }
        )

        self.assertTrue(form.is_valid())

    def test_task_form(self):
        form = TaskForm(
            data={
                "name": "name1",
                "description": "description1",
                "deadline": self.deadline,
                "priority": self.priority,
                "status": self.status,
                "task_type": self.task_type.id
            }
        )

        print("Available task types:", dict(form.fields["task_type"].choices))

        self.assertTrue(form.is_valid())

    def test_comment_form(self):
        form = CommentForm(
            data={
                "message": "test comment"
            }
        )

        self.assertTrue(form.is_valid())

    def test_project_task_search_form(self):
        form = ProjectTaskSearchForm(
            data={
                "title": "test12"
            }
        )

        self.assertTrue(form.is_valid())

    def test_profile_form(self):
        form = ProfileForm(
            data={
                "first_name": "test_first",
                "last_name": "test_last",
                "email": "email@email.email",
                "position": self.position.id,
                "profile_image": "test_pic.png"
            }
        )

        self.assertTrue(form.is_valid())
