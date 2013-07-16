__author__ = 'PervinenkoVN'

from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
import re
import json

def login_handler(r):
    if r.method != 'POST':
        return HttpResponse(get_json_response(code=1, message='GET method in invalid for this request'))
    if 'login' not in r.POST or 'pwd' not in r.POST:
        return HttpResponse(get_json_response(code=2, message='Parameters required'))
    uid = re.sub('\W+', '', r.POST['login'])
    password = r.POST['pwd']
    user = authenticate(username=uid, password=password)
    if user is not None:
        if user.is_active:
            login(r, user)
        else:
            return HttpResponse(get_json_response(code=3, message='Account is disabled'))
    else:
        return HttpResponse(get_json_response(code=4, message='Login failed'))
    return HttpResponse(get_json_response(code=0, values = {'username' : user.username }))

def get_json_response(code, values = {} , message = ''):
    values['code'] = code
    values['message'] = message
    return json.dumps(values)

