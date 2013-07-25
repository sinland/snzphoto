from django.conf.urls import patterns, include, url
from news import views as news_views
from snzphoto import ajax, views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', news_views.index),
    url(r'^news/', include('news.urls', namespace='news')),
    url(r'^video/', include('videos.urls', namespace='videos')),
    url(r'^gallery/', include('photos.urls', namespace='photos')),
    url(r'^management/', include('mngmnt.urls', namespace='management')),
    url(r'^login/$', ajax.login_handler, name='login_handler'),
    url(r'^logout/$', views.logout_action, name='logout_handler'),
)

#handler404 = 'snzphoto.views.page_not_found'
#handler500 = 'snzphoto.views.server_error'