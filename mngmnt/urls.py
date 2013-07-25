from django.conf.urls import patterns, url
from mngmnt import news_views, photos_views, video_views, debates_views, members_views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', news_views.index, name='index'),
    url(r'^news/$', news_views.index, name='news_index'),
    url(r'^news/page/(?P<page>\d+)$', news_views.index, name='news_paged_index'),
    url(r'^news/add/$', news_views.add_article, name='news_add'),
    url(r'^news/(?P<news_id>\d+)/edit/$', news_views.edit_article, name='news_edit'),
    url(r'^news/(?P<news_id>\d+)/delete/$', news_views.delete_article, name='news_delete'),
    url(r'^news/upload-attach/$', news_views.attachment_upload, name='news_media_reciever'),
    url(r'^news/delete-attach/$', news_views.attachment_remove, name='news_media_eraser'),

    url(r'^albums/$', photos_views.index, name='albums_index'),
    url(r'^albums/page/(?P<page>\d+)$', photos_views.index, name='albums_paged_index'),
    url(r'^albums/create/$', photos_views.create, name='albums_create'),
    url(r'^albums/(?P<aid>\d+)/delete/$', photos_views.delete, name='albums_delete'),
    url(r'^albums/(?P<aid>\d+)/edit/$', photos_views.edit, name='albums_edit'),
    url(r'^albums/(?P<aid>\d+)/photos/$', photos_views.get_photos, name='albums_photos'),
    url(r'^albums/(?P<aid>\d+)/upload-photos/$', photos_views.upload_photos, name='albums_uploads'),
    url(r'^albums/(?P<aid>\d+)/uploader-recieve/$', photos_views.upload_photo_handler, name='albums_upload_recieve'),
    url(r'^albums/(?P<aid>\d+)/uploader-delete/$', photos_views.upload_photo_delete, name='albums_upload_delete'),
    url(r'^albums/(?P<aid>\d+)/uploader-save/$', photos_views.upload_photo_save, name='albums_upload_save'),
    url(r'^albums/(?P<aid>\d+)/photo/(?P<pid>\d+)/edit/', photos_views.edit_photo, name='albums_photo_update'),
    url(r'^albums/(?P<aid>\d+)/photo/(?P<pid>\d+)/delete/$', photos_views.delete_photo, name='albums_photo_delete'),

    url(r'^video/$', video_views.index, name='video_index'),
    url(r'^video/page/(?P<page>\d+)$', video_views.index, name='video_paged_index'),
    url(r'^video/add/$', video_views.add_article, name='video_add'),
    url(r'^video/(?P<id>\d+)/edit/$', video_views.edit_article, name='video_edit'),
    url(r'^video/(?P<id>\d+)/delete/$', video_views.delete_article, name='video_delete'),

    url(r'^debates/$', debates_views.index, name='debates_index'),
    url(r'^debates/page/(?P<page>\d+)$', debates_views.index, name='debates_paged_index'),

    url(r'^members/$', members_views.index, name='members_index'),
    url(r'^members/page/(?P<page>\d+)$', members_views.index, name='members_paged_index'),
    url(r'^members/add/$', members_views.add, name='member_add'),
    url(r'^members/(?P<mid>\d+)/edit/$', members_views.edit, name='member_edit'),
    url(r'^members/(?P<mid>\d+)/delete/$', members_views.delete, name='member_delete'),
)
