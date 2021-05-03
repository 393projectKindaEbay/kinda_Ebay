from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create your forms here.

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    error = ''
    def clean_email(self):
        original_email = self.cleaned_data.get('email')
        if not original_email.endswith('case.edu'):
            raise forms.ValidationError("Only @case.edu email addresses are allowed")


        return original_email

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            self.add_error(None, "password is too short")
            raise forms.ValidationError("password is too short")
        return password

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user