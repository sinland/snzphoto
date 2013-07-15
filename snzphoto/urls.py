from django.conf.urls import patterns, include, url
from news import views as news_views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', news_views.index),
    url(r'^news/', include('news.urls', namespace='news')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

handler404 = 'snzphoto.views.page_not_found'
handler500 = 'snzphoto.views.server_error'