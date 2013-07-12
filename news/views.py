from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response


# Create your views here.
def index(r):
    var1 = 'Hello World???'
    return render_to_response('news/index.html', locals())