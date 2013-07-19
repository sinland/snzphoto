# -*- coding: utf-8 -*-

from django import forms
from news.models import *

class NewsPostForm(forms.Form):
    title = forms.CharField(max_length=256, label=u'Заголовок', widget=forms.TextInput())
    text = forms.CharField(widget=forms.Textarea)
    uid = forms.CharField(max_length=128, label=u'URL', required=False)
