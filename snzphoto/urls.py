from django.conf.urls import patterns, include, url
from news import views as news_views
from snzphoto import ajax, views

urlpatterns = patterns('',
    url(r'^$', views.intro, name='intro'),
    url(r'^events/$', news_views.index, name='site_root'),
    url(r'^events/', include('news.urls', namespace='news')),
    url(r'^video/', include('videos.urls', namespace='videos')),
    url(r'^gallery/', include('photos.urls', namespace='photos')),
    url(r'^forum/', include('debates.urls', namespace='debates')),
    url(r'^admin/', include('mngmnt.urls', namespace='management')),
    url(r'^login/$', views.login_action, name='login_page'),
    url(r'^logout/$', views.logout_action, name='logout_handler'),
    url(r'^badbrowser.html$', views.bad_browser, name='bad_browser')
)
