# -*- coding: utf-8 -*-
from django.shortcuts import render

__author__ = 'PervinenkoVN'

def index(request):
    return render(request, 'management/debates/index.html', {'section' : 'debates'})