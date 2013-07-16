from django import forms
from news.models import *

class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
