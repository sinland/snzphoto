from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect, render
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
def details(request, aid):
    return None