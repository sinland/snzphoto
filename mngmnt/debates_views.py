# -*- coding: utf-8 -*-

import random
import re
import json
import logging
import hashlib
import datetime
from django.template import RequestContext
from django.template.loader import render_to_string
from snzphoto import settings
from PIL import Image
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage as fs
from debates.models import *
from mngmnt.models import DebatesPostForm
from django.utils.html import escape

__author__ = 'PervinenkoVN'

log = logging.getLogger(name='manager.debates_views')

@never_cache
def index(request, page = 1):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    paginator = Paginator(DiscussionPost.objects.all().order_by('-creation_date', 'author'), 15)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'management/debates/index.html', {
        'posts' : posts,
        'section' : 'debates',
        'total_count' : DiscussionPost.objects.count()
    })

@never_cache
def add(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    result = None
    if request.method == 'GET':
        result = render(request, 'management/debates/add.html',{
            'form' : DebatesPostForm(),
            'section' : 'debates'
        })
    elif request.method == 'POST':
        form = DebatesPostForm(request.POST)
        uid = file_base = file_ext = uploaded_file = uploaded_thumb_file = None

        if 'uid' in request.POST and len(request.POST['uid']) > 0:
            if re.match('[a-zA-Z0-9]+', request.POST['uid']):
                uid = request.POST['uid']
                if uid in request.session:
                    file_base = request.session[uid][0]
                    uploaded_thumb_file = request.session[uid][2]
                    uploaded_file = request.session[uid][1]
                    file_ext = request.session[uid][3]

        if not form.is_valid():
            result = render(request, 'management/debates/add.html',{
                'form' : form,
                'section' : 'debates',
                'uid' : uid,
                'thumb_url' : uploaded_thumb_file
            })
        else:
            post = DiscussionPost(
                author=request.user,
                title=escape(form.cleaned_data['title']),
                text=form.cleaned_data['text']
            )
            trash = list()
            if file_base:
                post.attach = '%s.%s' % (file_base, file_ext)
                post.attach_thumb = 'thumb_%s.jpg' % file_base

                # переместим сам файл из uploads на его место
                if fs.exists(uploaded_file):
                    f = fs.open(uploaded_file)
                    fs.save(post.attach_path(), f)
                    f.close()
                    trash.append(uploaded_file)
                else:
                    post.attach = ""

                #переместим файл эскиза из uploads на его место
                if fs.exists(uploaded_thumb_file):
                    f = fs.open(uploaded_thumb_file)
                    fs.save(post.attach_thumb_path(), f)
                    f.close()
                    trash.append(uploaded_thumb_file)

                del request.session[uid]

            post.save()
            result = redirect('management:debates_index')
            for tfile in trash:
                if fs.exists(tfile):
                    try:
                        fs.delete(tfile)
                    except IOError as e:
                        log.error("Failed to delete file '%s'. %s" % (tfile, e.message))
    return result

@never_cache
def edit(request, id):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    post = get_object_or_404(DiscussionPost, pk=id)

    if request.method == 'GET':
        return render(request, 'management/debates/edit.html',{
            'form' : DebatesPostForm(initial={
                'title' : post.title,
                'text' : post.text,
            }),
            'post' : post,
            'section' : 'debates'
        })
    elif request.method == 'POST':
        form = DebatesPostForm(request.POST)
        try:
            if form.is_valid():
                post.title = form.cleaned_data['title']
                post.text = form.cleaned_data['text']

                trash = list()
                if 'flag_rm_attach' in request.POST and len(request.POST['flag_rm_attach']) > 0:
                    trash.append(post.attach_path())
                    trash.append(post.attach_thumb_path())
                    post.attach = ""
                    post.attach_thumb = ""

                if 'uid' in request.POST and len(request.POST['uid']) > 0:
                    if not re.match('[a-zA-Z0-9]+', request.POST['uid']):
                        form.errors[u'title'] = u'Ошибка загрузки файла. Перезагрузите страницу и повторите операцию!'
                        raise ValueError
                    uid = request.POST['uid']
                    if not uid in request.session:
                        form.errors[u'title'] = u'Ошибка загрузки файла. Сессия истекла. Перезагрузите страницу и повторите операцию!'
                        raise ValueError

                    file_base = request.session[uid][0]
                    uploaded_thumb_file = request.session[uid][2]
                    uploaded_file = request.session[uid][1]
                    file_ext = request.session[uid][3]

                    del request.session[uid]

                    if fs.exists(uploaded_file):
                        post.attach = "%s.%s" % (file_base, file_ext)
                        f = fs.open(uploaded_file)
                        fs.save(post.attach_path(), f)
                        f.close()
                        trash.append(uploaded_file)

                    if fs.exists(uploaded_thumb_file):
                        post.attach_thumb = "thumb_%s.jpg" % file_base
                        f = fs.open(uploaded_thumb_file)
                        fs.save(post.attach_thumb_path(), f)
                        f.close()
                        trash.append(uploaded_thumb_file)

                post.save()
                for tfile in trash:
                    if fs.exists(tfile):
                        try:
                            fs.delete(tfile)
                        except IOError as e:
                            log.error("Failed to delete file '%s'. %s" % (tfile, e.message))
            else:
                raise ValueError
        except ValueError:
            return render(request, 'management/debates/edit.html',{
                'form' : form,
                'post' : post,
                'section' : 'debates'
            })

    return redirect('management:debates_index')

@never_cache
def delete(request, id):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    result = redirect('management:debates_index')
    post = get_object_or_404(DiscussionPost, pk=id)
    if request.method == 'GET':
        result = render(request, "management/debates/delete.html", {'post' : post, 'section' : 'debates'})
    elif request.method == "POST":
        for c in post.get_comments():
            c.delete()
        trash = list()
        if len(post.attach) > 0:
            trash.append(post.attach_path())
        if len(post.attach_thumb) > 0:
            trash.append(post.attach_thumb_path())

        post.delete()
        for tfile in trash:
            if fs.exists(tfile):
                try:
                    fs.delete(tfile)
                except IOError as e:
                    log.error("Failed to delete file '%s'. %s" % (tfile, e.message))
    return result

@never_cache
def attach_upload(request):
    if not request.user.is_authenticated():
        return HttpResponse(get_script_response(code=403, message='Unauthorized'))

    if 'userfile' not in request.FILES:
        return HttpResponse(get_script_response(code=400, message='File expected'))

    f = request.FILES['userfile']     # file is present only if request method is POST and form type was specified
    if not f.content_type.startswith('image/'):
        return HttpResponse(get_script_response(code=400, message='File format not supported!'))

    hash_base = "%s-%s-%s-%s" % (f.name, datetime.datetime.now().isoformat(' '), request.META['HTTP_USER_AGENT'], request.META['REMOTE_ADDR'])
    fname_base = hashlib.md5(hash_base.encode('utf-8')).hexdigest()
    ext = f.name.split('.')[-1]
    if len(ext) > 5:
        ext = ext[0:2]
    full_file = "uploads/%s.%s" % (fname_base, ext)
    thumb_file = 'uploads/thumb_%s.jpg' % fname_base

    log.debug("Generated name for upload: %s" % fname_base)
    log.debug("Generated filename for thumbnail: %s" % thumb_file)

    fs.save(full_file, f)

    try:
        im = Image.open(fs.path(full_file))
        im.thumbnail(settings.IMG_THUMBS_SIZE, Image.ANTIALIAS)
        im.save(fs.path(thumb_file), "JPEG")
    except IOError as e:
        log.error("Failed to create thumbnail. %s" % e.message)
        fs.save(thumb_file, f)

    #save names in session
    uid = generate_uid()
    while uid in request.session:
        uid = generate_uid()

    request.session[uid] = (fname_base, full_file, thumb_file, ext)

    #return url to it
    response = HttpResponse(
        get_script_response(code=0,
            message=uid,
            thumb_url=fs.url(thumb_file)
        )
    )
    return response

@never_cache
def attach_delete(request):
    if not request.user.is_authenticated():
        return HttpResponse(get_json_response(code=403, message='Unauthorized'))

    try:
        if 'uid' in request.POST and len(request.POST['uid']) > 0:
            if not re.match('[a-zA-Z0-9]+', request.POST['uid']):
                raise ValueError(u'Передано некорректное имя файла')
            uid = request.POST['uid']
            if not uid in request.session:
                raise ValueError(u'Сессия завершена!')

            uploaded_file = request.session[uid][1]
            thumb_file = request.session[uid][2]

            del request.session[uid]

            if fs.exists(uploaded_file):
                try:
                    fs.delete(uploaded_file)
                except IOError as e:
                    log.error("Failed to delete file '%s'. %s" % (uploaded_file, e.message))
            if fs.exists(thumb_file):
                try:
                    fs.delete(thumb_file)
                except IOError as e:
                    log.error("Failed to delete file '%s'. %s" % (thumb_file, e.message))
    except ValueError as e:
        HttpResponse(get_json_response(code=400, message=e.message))
    return HttpResponse(get_json_response(code=200))


def get_json_response(code, values = {} , message = ''):
    values['code'] = code
    values['message'] = message
    return json.dumps(values)


def get_script_response(code, message='', thumb_url=''):
    return '<script type="text/javascript">window.top.window.onUploadFinished(%s, "%s", "%s");</script>' %\
           (code, message, thumb_url)

def generate_uid():
    result = ""
    for i in range(6):
        result += "%x" % random.randint(0, 15)
    return "id%s" % result
