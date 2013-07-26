# -*- coding: utf-8 -*-

__author__ = 'PervinenkoVN'

from django.conf.urls import patterns, url
from photos import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^p/(?P<page>\d{1,10})/$', views.index, name='paged_index'),
    url(r'^(?P<id>\d+)/$', views.details, name='details'),
    url(r'^(?P<id>\d+)/photo/(?P<pid>\d+)$', views.details, name='details_sel_photo'),
)

