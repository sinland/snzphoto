__author__ = 'PervinenkoVN'

from django.conf.urls import patterns, include, url
from news import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'snzphoto.views.home', name='home'),
    url(r'^$', views.index, name='index'),
    url(r'^p/(?P<page>\d{1,10})/$', views.index, name='paged_index'),
    url(r'^(?P<post_uid>.*)\.html$', views.show_post, name='show_post')

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

