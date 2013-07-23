# -*- coding: utf-8 -*-

from PIL import Image
import re
import json
import logging
import hashlib
import datetime
from time import sleep
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache, cache_control
from django.core.files.storage import default_storage as fs
from django.core.cache import cache
from mngmnt.models import *
from photos.models import *
from snzphoto.utils import get_json_response

@never_cache
def index(request, page=1):
    if not request.user.is_authenticated():
        return redirect('news:index')
    paginator = Paginator(PhotoAlbum.objects.all().order_by('-creation_date', 'author'), 20)
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        albums = paginator.page(1)
    except EmptyPage:
        albums = paginator.page(paginator.num_pages)

    return render(request, 'management/albums/index.html', {
        'albums' : albums,
        'section' : 'albums',
        'total_count' : PhotoAlbum.objects.count()
    })

@never_cache
def create(request):
    if not request.user.is_authenticated():
        return redirect('news:index')
    response = None
    if request.method == 'GET':
        response = render(request, 'management/albums/create.html', {'section' : 'albums', 'form' : AlbumEditForm })
    elif request.method == 'POST':
        form = AlbumEditForm(request.POST)
        if not form.is_valid():
            response = render(request, 'management/albums/create.html', {'section' : 'albums', 'form' : form })
        else:
            album = PhotoAlbum(author=request.user, title=form.cleaned_data['title'], description=form.cleaned_data['description'],
                views_counter = 0)
            album.save()
            response = redirect('management:albums_index')
    else:
        response = redirect('management:albums_index')
    return response

@never_cache
def edit(request, aid):
    if not request.user.is_authenticated():
        return redirect('news:index')
    response = None
    try:
        album = PhotoAlbum.objects.get(pk=aid)
        if request.method == 'GET':
            response = render(request,
                'management/albums/edit.html', {
                    'section' : 'albums',
                    'album': album,
                    'form' : AlbumEditForm(initial={
                        'title' : album.title,
                        'description' : album.description
                    })
                })
        else:
            pass
            response = redirect('management:albums_index')
    except PhotoAlbum.DoesNotExist:
        response = redirect('management:albums_index')
    return response

@never_cache
def delete(request, aid):
    if not request.user.is_authenticated():
        return redirect('news:index')
    response = None
    try:
        album = PhotoAlbum.objects.get(pk=aid)
        if request.method == 'GET':
            response = render(request, 'management/albums/delete.html', {'section' : 'albums', 'album': album})
        else:
            for photo in album.get_photos():
                for f in (photo.get_file_path(), photo.get_thumb_path()):
                    if fs.exists(f):
                        try:
                            fs.delete(f)
                        except IOError:
                            #todo: add error message to log
                            pass
                photo.delete()
            album.delete()
            response = redirect('management:albums_index')
    except PhotoAlbum.DoesNotExist:
        response = redirect('management:albums_index')
    return response

@never_cache
def get_photos(request, aid):
    if not request.user.is_authenticated():
        return get_json_response(code=403)

    response = None
    try:
        album = PhotoAlbum.objects.get(pk=aid)
        pics = list()
        for p in album.get_photos():
            pics.append(json.dumps({
                'thumb_url' : fs.url(p.get_thumb_path()),
                'url': fs.url(p.get_file_path()),
                'description' : p.description,
                'author' : p.author
            }))
        response = get_json_response(code=200, values={'photos' : pics})
    except PhotoAlbum.DoesNotExist:
        response = get_json_response(code=404)
    return response

@never_cache
def upload_photos(request, aid):
    if not request.user.is_authenticated():
        return redirect('news:index')

    response = None
    try:
        album = PhotoAlbum.objects.get(pk=aid)
        response = render(request, 'management/albums/upload_photos.html', {'section' : 'albums', 'album' : album})
    except PhotoAlbum.DoesNotExist:
        response = redirect('news:index')

    return response

@never_cache
def upload_photo_handler(request, aid):
    if not request.user.is_authenticated():
        return get_json_response(403)

    if 'request_id' in request.POST:
        rid = request.POST['request_id']
    else:
        return get_json_response(400, message='Expected value of RID not found')

    if 'userfile' not in request.FILES:
        return get_script_response(code=400, rid=rid, uid='File expected', thumb_url='')

    f = request.FILES['userfile']
    if not f.content_type.startswith('image/'):
        return get_script_response(code=400, rid=rid, uid='File format not supported', thumb_url='')

    hash_base = "%s-%s-%s-%s" % (f.name, datetime.datetime.now().isoformat(' '), request.META['HTTP_USER_AGENT'], request.get_host())
    uid = hashlib.sha1(hash_base).hexdigest()
    ext = f.name.split('.')[-1]
    if len(ext) > 5:
        ext = ext[0:2]
    img_file = "uploads/%s.%s" % (uid, ext)
    img_thumb_file = 'uploads/thumb%s.jpg' % uid

    fs.save(img_file, f)

    try:
        im = Image.open(fs.path(img_file))
        im.thumbnail((150, 150), Image.ANTIALIAS)
        im.save(fs.path(img_thumb_file), "JPEG")
    except IOError:
        fs.save(img_thumb_file, f)

    cache.set(uid, (img_file, img_thumb_file))

    return get_script_response(200, rid, uid, fs.url(img_thumb_file))

@never_cache
def upload_photo_delete(request, aid):
    if not request.user.is_authenticated():
        return get_json_response(code=403)

    response = None
    if request.method == 'POST':
        if 'uid' in request.POST:
            uid = request.POST['uid']
            if re.match('^[a-zA-Z0-9]+$', uid):
                trash = cache.get(uid)
                if trash is not None:
                    cache.delete(uid)
                    for f in trash:
                        if fs.exists(f):
                            try:
                                fs.delete(f)
                            except IOError:
                                pass
                response = get_json_response(code=200)
            else:
                response = get_json_response(code=400, message=u'Bad filename')
        else:
            response = get_json_response(code=400, message=u'UID expected')
    else:
        response = get_json_response(code=405, message='POST please')
    return response

@never_cache
def upload_photo_save(request, aid):
    if not request.user.is_authenticated():
        return get_json_response(code=403)
    if request.method != 'POST':
        return get_json_response(code=405, message='POST please')
    try:
        album = PhotoAlbum.objects.get(pk=aid)
    except PhotoAlbum.DoesNotExist:
        return get_json_response(code=404, message='Album not found')

    if 'uid' not in request.POST:
        return get_json_response(code=400, message=u'UID expected')
    uid = request.POST['uid']
    if not re.match('^[a-zA-Z0-9]+$', uid):
        response = get_json_response(code=400, message=u'Bad filename')

    uploads = cache.get(uid)
    if uploads is None:
        return get_json_response(code=400, message=u'Request not found by token ID')

    cache.delete(uid)
    uploaded_file = uploads[0]
    uploaded_thumb = uploads[1]
    if not fs.exists(uploaded_file) or not fs.exists(uploaded_thumb):
        return get_json_response(code=400, message=u'Files not found')

    ext = uploaded_file.split('.')[-1]
    foto = Photo(album=album,
        filename='%s.%s' % (uid, ext),
        thumbfile='%s.jpg' % uid,
        description='',
        author='',
        likes_count=0)

    trash = []
    f = fs.open(uploaded_file)
    fs.save(foto.get_file_path(), f)
    f.close()
    trash.append(uploaded_file)

    f = fs.open(uploaded_thumb)
    fs.save(foto.get_thumb_path(), f)
    f.close()
    trash.append(uploaded_thumb)

    for tfile in trash:
        if fs.exists(tfile):
            try:
                fs.delete(tfile)
            except IOError:
                pass

    foto.save()

    return get_json_response(code=200)

@never_cache
def update_photo(request, aid, pid):
    return None

@never_cache
def delete_photo(request, aid, pid):
    return None

def get_script_response(code, rid, uid, thumb_url):
    return HttpResponse(
        "<script type=\"text/javascript\">window.top.window.onUploadComplete(%s, '%s', '%s', '%s');</script>" %\
                        (code, rid, uid, thumb_url))


