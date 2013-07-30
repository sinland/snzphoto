# -*- coding: utf-8 -*-

from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

__author__ = 'PervinenkoVN'
from django.http import HttpResponse

def logout_action(r):
    logout(r)
    return HttpResponseRedirect(reverse('news:index'))


def bad_browser(request):
    return render(request, 'badbrowser.html')


#todo: нужен отдельный файл под крон-задание для очистки каталога uploads, например ночью с воскресенья на понедельник