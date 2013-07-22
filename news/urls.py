__author__ = 'PervinenkoVN'

from django.conf.urls import patterns, include, url
from news import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^p/(?P<page>\d{1,10})/$', views.index, name='paged_index'),
    url(r'^(?P<post_uid>.*)\.html$', views.show_post, name='show_post'),
    url(r'^(?P<pid>\d+)/get-comments/$', views.get_comments, name='get_comments'),
    url(r'^(?P<pid>\d+)/add-comment/$', views.add_comment, name='add_comment'),
    url(r'^(?P<pid>\d+)/delete-comment/$', views.delete_comment, name='delete_comment'),
)

