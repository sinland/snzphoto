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

    section = "photo"

    if albums.number - 1 > 2:
        first_page = 1 # первая страница стоит отдельно
    if paginator.num_pages - albums.number > 3:
        last_page = paginator.num_pages # последняя страница стоит отдельно
    pages_range = paginator.page_range[albums.number:albums.number+3]
    left_range = albums.number-3
    if left_range < 0:
        left_range = 0
    for p in paginator.page_range[left_range:albums.number]:
        pages_range.append(p)
    pages_range.sort()

    response = render(request, 'photos/index.html', locals())
    response.set_cookie('last_viewed_gallerypage', page)
    return response

@never_cache
def details(request, id, photo_indx=0):
    album = get_object_or_404(PhotoAlbum, pk=id)
    album.views_counter += 1;
    album.save()
    last_viewed_gallerypage = 1
    if 'last_viewed_gallerypage' in request.COOKIES:
        last_viewed_gallerypage = request.COOKIES['last_viewed_gallerypage']

    cur_photo_indx = int(photo_indx)
    all_photos = album.get_photos()

    prev_i = None
    if (cur_photo_indx - 1) >= 0:
        prev_i = cur_photo_indx - 1

    next_i = None
    if cur_photo_indx + 1 < len(all_photos):
        next_i = cur_photo_indx + 1

    photo = None
    if len(all_photos) > 0:
        if cur_photo_indx >= 0:
            photo = all_photos[cur_photo_indx]
        else:
            photo = all_photos[0]

    return render(request, 'photos/album_details.html', {
        'next_i': next_i,
        'prev_i': prev_i,
        'last_viewed_gallerypage' : last_viewed_gallerypage,
        'album' : album,
        'photo' : photo,
        'section' : "photo"
    })