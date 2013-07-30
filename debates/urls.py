# -*- coding: utf-8 -*-
__author__ = 'PervinenkoVN'

from django.conf.urls import patterns, url
from debates import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^p/(?P<page>\d+)/$', views.index, name='paged_index'),
    url(r'^(?P<id>\d+)/$', views.details, name='details'),
    url(r'^(?P<id>\d+)/get-comments/$', views.get_comments, name='get_comments'),
    url(r'^(?P<id>\d+)/add-comment/$', views.add_comment, name='add_comment'),
    url(r'^(?P<id>\d+)/delete-comment/$', views.delete_comment, name='delete_comment'),
)

