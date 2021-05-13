import datetime
import re
from unittest import mock

from django.contrib.auth.forms import (
    AdminPasswordChangeForm, AuthenticationForm, PasswordChangeForm,
    PasswordResetForm, ReadOnlyPasswordHashField, ReadOnlyPasswordHashWidget,
    SetPasswordForm, UserChangeForm, UserCreationForm,
)
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_login_failed
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.forms.fields import CharField, Field, IntegerField
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import translation
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from .forms import NewUserForm

 
 
class TestDataMixin:

    @classmethod
    def setUpTestData(cls):
        cls.u1 = User.objects.create_user(username='testuser', password='mytestpassword', email='testUser@case.edu')
        cls.u2 = User.objects.create_user(username='inuser', password='inpassword', email='inuser@case.edu', is_active=False)


 
 
class UserCreationFormTest(TestDataMixin, TestCase):
 
    def test_user_already_exists(self):
        data = {
            'username': 'testuser',
            'password1': 'test1234',
            'password2': 'test1234',
        }
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["username"].errors,
                        [str(User._meta.get_field('username').error_messages['unique'])])
 
    def test_invalid_user1(self):
        """
        invalid if user name contains punctuation
        """
        data = {
            'username': 'user!!',
            'password1': 'user123456',
            'password2': 'user123456',
        }
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        validator = next(v for v in User._meta.get_field('username').validators if v.code == 'invalid')
        self.assertEqual(form["username"].errors, [str(validator.message)])

    def test_invalid_user2(self):
        """
        invalid if user name contains punctuation
        """
        data = {
            'username': 'user_??',
            'password1': 'user123456',
            'password2': 'user123456',
        }
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        validator = next(v for v in User._meta.get_field('username').validators if v.code == 'invalid')
        self.assertEqual(form["username"].errors, [str(validator.message)])

    def test_password_verification(self):
        # The verification password is incorrect.
        data = {
            'username': 'user',
            'password1': 'user123',
            'password2': 'testuser123',
        }
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["password2"].errors,
                         [str(form.error_messages['password_mismatch'])])


    def test_valid_email_case1(self):
        data = {
            'username': 'user',
            'password1': 'testuser123',
            'password2': 'testuser123',
            'email': 'user@user.com', 
        }
        form = NewUserForm(data)
        self.assertIn('Only @case.edu email addresses are allowed', form['email'].errors)

    def test_valid_email_case2(self):
        data = {
            'username': 'user',
            'password1': 'testuser123',
            'password2': 'testuser123',
            'email': 'user@user.edu', 
        }
        form = NewUserForm(data)
        self.assertIn('Only @case.edu email addresses are allowed', form['email'].errors)

    def test_common_password(self): 
        data = {
            'username': 'user',
            'password1': 'hello12345',
            'password2': 'hello12345',
            'email': 'user@case.edu', 
        }
        form = NewUserForm(data)
        self.assertEqual(len(form['password2'].errors), 1)
        self.assertIn(
            'This password is too common.',
            form['password2'].errors
        )


    def test_both_passwords(self):
        # One (or both) passwords weren't given
        data = {'username': 'anaUser'}
        form = NewUserForm(data)
        required_error = [str(Field.default_error_messages['required'])]
        self.assertFalse(form.is_valid())
        self.assertEqual(form['password1'].errors, required_error)
        self.assertEqual(form['password2'].errors, required_error)

        data['password2'] = 'testUser123'
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['password1'].errors, required_error)
        self.assertEqual(form['password2'].errors, [])


    def test_validate_password_length(self):
        data = {
            'username': 'testuser',
            'password1': 'welwel',
            'password2': 'welwel',
        }
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['password2'].errors), 1)
        self.assertIn(
            'This password is too short. It must contain at least 8 characters.',
            form['password2'].errors
        )

    def test_validates_password_common_and_short(self):
        data = {
            'username': 'testuse',
            'password1': 'asdf',
            'password2': 'asdf',
        }
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['password2'].errors), 2)
        self.assertIn('This password is too common.', form['password2'].errors)
        self.assertIn(
            'This password is too short. It must contain at least 8 characters.',
            form['password2'].errors
        )

    def test_validates_password_similar_and_short(self):
        data = {
            'username': 'testuse',
            'password1': 'testuse',
            'password2': 'testuse',
        }
        form = NewUserForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['password2'].errors), 2)
        self.assertIn('The password is too similar to the username.', form['password2'].errors)
        self.assertIn(
            'This password is too short. It must contain at least 8 characters.',
            form['password2'].errors
        )

    def test_normal_register(self): 
        data = {
            'username': 'testuser',
            'password1': 'hello123456',
            'password2': 'hello123456',
            'email': 'hello@case.edu'
        }
        form = NewUserForm(data)
        response = self.client.post('/home/')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Registration successful.')

class UserSigninTest(TestDataMixin, TestCase):
    def test_invalid_username(self):
        # The user submits an invalid username.

        data = {
            'username': 'userNotExists',
            'password': 'testuser',
        }
        form = AuthenticationForm(None, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), [
                form.error_messages['invalid_login'] % {
                    'username': User._meta.get_field('username').verbose_name
                }
            ]
        )

    def test_normal_login(self): 
        data = {
            'username': 'testuser',
            'password1': 'mytestpassword',
        }
        form = AuthenticationForm(None, data)
        response = self.client.post('/')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

    def test_invalid_fassword(self):
        # The user submits an invalid password.

        data = {
            'username': 'testuser',
            'password': 'usertest1234',
        }
        form = AuthenticationForm(None, data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.non_field_errors(), [
                form.error_messages['invalid_login'] % {
                    'username': User._meta.get_field('username').verbose_name
                }
            ]
        )
