# -*- coding: utf-8 -*-
import re

from django.contrib.auth import logout, authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

__author__ = 'PervinenkoVN'
from django.http import HttpResponse

def logout_action(r):
    logout(r)
    return HttpResponseRedirect(reverse('intro'))


def bad_browser(request):
    return render(request, 'badbrowser.html')


def intro(request):
    return render(request, 'intro.html')

#todo: нужен отдельный файл под крон-задание для очистки каталога uploads, например ночью с воскресенья на понедельник

def login_action(request):
    if request.method == 'GET':
        if not request.user.is_authenticated():
            return render(request, 'login.html')
        else :return HttpResponseRedirect(reverse('site_root'))
    try:
        if 'username' not in request.POST:
            raise ValueError('Укажите логин')
        if len(request.POST['username']) == 0:
            raise ValueError('Логин не может быть пустым')
        if 'password' not in request.POST:
            raise ValueError('Укажите пароль')
        if len(request.POST['password']) == 0:
            raise ValueError('Пароль не может быть пустым')

        uid = re.sub('\W+', '', request.POST['username'])
        password = request.POST['password']
        user = authenticate(username=uid, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                raise ValueError('Учетная запись отключена')
        else:
            raise ValueError('Указаны неверные учетные данные')
    except ValueError as e:
        return render(request, 'login.html', {'error' : e.message})

    return HttpResponseRedirect(reverse('site_root'))