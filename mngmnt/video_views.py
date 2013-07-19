# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render

__author__ = 'PervinenkoVN'

def index(request):
    return render(request, 'management/video/index.html', {'section' : 'video'})