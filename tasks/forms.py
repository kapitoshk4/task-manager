from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    UsernameField,
    PasswordResetForm,
    SetPasswordForm
)
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from tasks.models import Project, ChatMessage, Worker, Task, TaskComment, TaskType


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput
                                (attrs={
                                    "class": "form-control",
                                    "placeholder": "Password"
                                }))
    password2 = forms.CharField(label="Password",
                                widget=forms.PasswordInput
                                (attrs={
                                    "class": "form-control",
                                    "placeholder": "Confirm password"
                                }))

    class Meta:
        model = Worker
        fields = ("username", "email", "first_name", "last_name", "position",)

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email"
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First name"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last name"
            }),
            "position": forms.Select(attrs={
                "class": "form-control",
                "placeholder": "Position"
            })
        }


class LoginForm(AuthenticationForm):
    username = UsernameField(label=_("Your Username"),
                             widget=forms.TextInput(attrs={
                                 "class": "form-control",
                                 "placeholder": "Username"
                             }))
    password = forms.CharField(
      label=_("Your Password"),
      strip=False,
      widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description"]

    title = forms.CharField(label=_("Title"),
                           widget=forms.TextInput(attrs={
                               "class": "form-control",
                               "placeholder": ""
                           }),
                           required=True)
    description = forms.CharField(label=_("Description"),
                                  widget=forms.Textarea(attrs={
                                      "class": "form-control",
                                      "placeholder": ""
                                  }),
                                  required=True)


class JoinProjectForm(forms.Form):
    invitation_code = forms.CharField(label=_("Invitation"),
                                      widget=forms.TextInput(attrs={
                                          "class": "form-control",
                                          "placeholder": ""
                                      }))

    def clean(self):
        super(JoinProjectForm, self).clean()

        invitation_code = self.cleaned_data.get("invitation_code")

        if len(invitation_code) != 36:
            self.add_error("invitation_code", "Ensure your invitation code is 32 characters long")


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ["message", ]

    message = forms.CharField(label=_("Message"),
                              widget=forms.TextInput(attrs={
                               "class": "form-control",
                               "placeholder": "Send message"
                              }))


class ProjectSearchForm(forms.Form):
    title = forms.CharField(max_length=100, required=False, label="", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Search . . .",
    }))


class TaskForm(forms.ModelForm):
    name = forms.CharField(
        error_messages={"required": "Please enter a name."},
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Name"
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Description"
        }),
        required=False
    )
    deadline = forms.DateField(
        error_messages={"required": "Please enter a deadline."},
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "placeholder": "Date of deadline",
            "type": "date"
        })
    )
    priority = forms.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "placeholder": "Priority"
        })
    )
    status = forms.ChoiceField(
        choices=Task.STATUS_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "placeholder": "Status"
        })
    )
    task_type = forms.ModelChoiceField(
        error_messages={"required": "Please enter a task type."},
        queryset=TaskType.objects.all(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "placeholder": "Task type"
        })
    )

    class Meta:
        model = Task
        fields = ["name", "description", "deadline", "priority", "status", "task_type"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ["message", ]

        labels = {"message": ""}

        widgets = {
            "message": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Add a comment..."
            }),
        }


class ProjectTaskSearchForm(forms.Form):
    title = forms.CharField(max_length=100, required=False, initial="", label="", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Search . . .",
    }))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["first_name", "last_name", "email", "position", "profile_image", ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First name"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email"
            }),
            "position": forms.Select(attrs={
                "class": "form-control",
                "placeholder": "Position"
            }),
            "profile_image": forms.FileInput(attrs={
                "class": "form-control",
                "placeholder": "File"
            })
        }
