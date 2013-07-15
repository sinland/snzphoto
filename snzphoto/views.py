__author__ = 'PervinenkoVN'
from django.http import HttpResponse

def page_not_found(r):
    return HttpResponse('Fail!')

def server_error(r):
    return HttpResponse('Fail!')
