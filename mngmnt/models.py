# -*- coding: utf-8 -*-

from django import forms
from custom_validators import login_validator

class NewsPostForm(forms.Form):
    title = forms.CharField(max_length=256, label=u'Заголовок', widget=forms.TextInput())
    text = forms.CharField(widget=forms.Textarea)
    uid = forms.CharField(max_length=128, label=u'URL', required=False)

class MemberForm(forms.Form):
    first_name = forms.CharField(max_length=128, label=u'Имя',required=False)
    last_name = forms.CharField(max_length=128, label=u'Фамилия',required=False)
    email = forms.EmailField(required=False, label=u'E-Mail')
    is_active = forms.BooleanField(label=u'Активность', required=False)
    is_staff = forms.BooleanField(label=u'Администратор', required=False)
    login = forms.CharField(max_length=64, required=False, validators=[login_validator])
    password = forms.CharField(min_length=8, max_length=64, required=False, widget=forms.PasswordInput())


