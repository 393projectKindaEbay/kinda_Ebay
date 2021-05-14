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
from .models import Product
from .forms import ProductForm

class productTest(TestCase):
    def test_title_length(self):
        data = {
            'title': 'This is a title with more than one hundred and twenty characters,\
            and this title should not be allowed to use, try to make the sentence shorter!!!!!',
            'description': 'Second-hand TV',
            'price' : '99.99',
            'summary':'Second-hand TV',
            'category':'1',
            'label':'1',
            'Product_Main_Img':''
        }
        form = ProductForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['title'].errors), 1)
        self.assertIn(
            'This title is too long. It must contain at most 120 characters.',
            form['title'].errors
        )

    def test_price_digits(self):
        data = {
            'title': 'This is a title',
            'description': 'Second-hand TV',
            'price' : '999999.99',
            'summary':'Second-hand TV',
            'category':'1',
            'label':'1',
            'Product_Main_Img':''
        }
        form = ProductForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['price'].errors), 1)
        self.assertIn(
            'This price can not be larger than 10000',
            form['price'].errors
        )

    def test_price_decimal(self):
        data = {
            'title': 'This is a title',
            'description': 'Second-hand TV',
            'price' : '99.9999',
            'summary':'Second-hand TV',
            'category':'1',
            'label':'1',
            'Product_Main_Img':''
        }
        form = ProductForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['price'].errors), 1)
        self.assertIn(
            'This price must have less than 2 decimal places',
            form['price'].errors
        )

    def test_no_such_label(self):
        data = {
            'title': 'This is a title',
            'description': 'Second-hand TV',
            'price' : '99.9',
            'summary':'Second-hand TV',
            'category':'1',
            'label':'5',
            'Product_Main_Img':''
        }
        form = ProductForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['label'].errors), 1)
        self.assertIn(
            'There is no such label',
            form['label'].errors
        )

    def test_no_such_category(self):
        data = {
            'title': 'This is a title',
            'description': 'Second-hand TV',
            'price' : '99.9',
            'summary':'Second-hand TV',
            'category':'5',
            'label':'1',
            'Product_Main_Img':''
        }
        form = ProductForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['category'].errors), 1)
        self.assertIn(
            'There is no such category',
            form['category'].errors
        )
    
