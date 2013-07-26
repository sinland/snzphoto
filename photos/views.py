# -*- coding: utf-8 -*-

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect, render, get_object_or_404
from photos.models import *
from snzphoto import settings

@never_cache
def index(request, page=1):
    paginator = Paginator(PhotoAlbum.objects.all().order_by('-creation_date', 'author'), settings.NEWS_PER_PAGE)
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        albums = paginator.page(1)
    except EmptyPage:
        albums = paginator.page(paginator.num_pages)

    response = render(request, 'photos/index.html', locals())
    response.set_cookie('last_viewed_gallerypage', page)
    return response

@never_cache
def details(request, id, pid=-1):
    album = get_object_or_404(PhotoAlbum, pk=id)
    album.views_counter += 1;
    album.save()
    last_viewed_gallerypage = 1
    if 'last_viewed_gallerypage' in request.COOKIES:
        last_viewed_gallerypage = request.COOKIES['last_viewed_gallerypage']
    photo = None
    if pid >= 0:
        photo = get_object_or_404(Photo, pk=pid)
    return render(request, 'photos/album_details.html', {
        'last_viewed_gallerypage' : last_viewed_gallerypage,
        'album' : album,
        'photo' : photo
    })