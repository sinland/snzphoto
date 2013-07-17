# -*- coding: utf-8 -*-

from django import forms
from news.models import *

class NewsPostForm(forms.Form):
    title = forms.CharField(max_length=256, label=u'Заголовок')
    text = forms.CharField(max_length=2048, widget=forms.Textarea)
    uid = forms.URLField(max_length=128, label=u'URL')
