__author__ = 'PervinenkoVN'

from django.conf.urls import patterns, url
from mngmnt import views, ajax

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.news_index, name='index'),
    url(r'^news/index/$', views.news_index, name='news_index'),
    url(r'^news/index/(?P<page>\d+)$', views.news_index, name='news_paged_index'),
    url(r'^news/add/$', views.news_add, name='news_add'),
    url(r'^news/(?P<news_id>\d+)/edit/$', views.news_edit, name='news_edit'), # get = read, post = update
    url(r'^news/(?P<news_id>\d+)/delete/$', views.news_delete, name='news_delete'),
    url(r'^news/(?P<news_id>\d+)/upload-picture/$', ajax.news_picture_upload_handler, name='news_media_reciever'),
)
