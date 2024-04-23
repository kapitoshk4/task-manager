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

from tasks.models import Project, ChatMessage


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


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]

    name = forms.CharField(label=_("Title"),
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
