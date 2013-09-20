# -*- coding: utf-8 -*-
import hashlib
import json
import logging
import re
import datetime
from django.http import HttpResponseForbidden, HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from snzphoto.utils import clean_embedded_video_link
from django.views.decorators.cache import never_cache, cache_control
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from videos.models import *
from mngmnt.models import *
from django.core.files.storage import default_storage as fs

__author__ = 'PervinenkoVN'
log = logging.getLogger(name='manager-videos')

@cache_control(must_revalidate=True)
def index(request, page=1):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    paginator = Paginator(VideoPost.objects.all().order_by('-creation_date', 'author'), 20)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    return render(request, 'management/video/index.html', {
        'videos' : videos,
        'section' : 'video',
        'total_count' : VideoPost.objects.count()
    })

@cache_control(must_revalidate=True)
def add_article(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    result = None
    if request.method == 'GET':
        result = render(request, 'management/video/add.html',{
            'form' : VideoPostForm(),
            'section' : 'news'
        })
    elif request.method == 'POST':
        form = VideoPostForm(request.POST)
        try:
            if form.is_valid():
                post = VideoPost(
                    author=request.user,
                    title=escape(form.cleaned_data['title']),
                    text=form.cleaned_data['text'],
                    link=clean_embedded_video_link(form.cleaned_data['link'])
                )
                if len(post.link) == 0:
                    form.errors['link'] = [u'Ссылка задана некорректно или данный тип ссылки не поддерживается.']
                    raise ValueError
                trash = []
                if len(form.cleaned_data['token_uid']) > 0:
                    fname_info =  request.session[form.cleaned_data['token_uid']]
                    if fname_info is not None:
                        del request.session[form.cleaned_data['token_uid']]
                        post.preview_img = fname_info[1]
                        if fs.exists(fname_info[0]):
                            f = fs.open(fname_info[0])
                            fs.save(post.get_preview_path(), f)
                            f.close()
                            trash.append(fname_info[0])

                post.save()
                result = redirect('management:video_index')
                for tfile in trash:
                    try:
                        fs.delete(tfile)
                    except IOError as err:
                        log.error("Failed to delete file '%s'. %s" % (tfile, err.message))
            else:
                raise ValueError
        except ValueError:
            result = render(request, 'management/video/add.html',{
                'form' : form,
                'section' : 'news',
                })
    return result

@cache_control(must_revalidate=True)
def edit_article(request, id):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    response = redirect('management:video_index')
    video = get_object_or_404(VideoPost, pk=id)
    if request.method == 'GET':
        response = render(request, 'management/video/edit.html',{
            'form' : VideoPostForm(initial={
                'title' : video.title,
                'text' : video.text,
                'link' : video.link,
                'uid' : video.uid
            }),
            'post' : video,
            'section' : 'video',
        })
    elif request.method == 'POST':
        form = VideoPostForm(request.POST)
        try:
            if form.is_valid():
                video.title = escape(form.cleaned_data['title'])
                video.text = form.cleaned_data['text']
                video.link = clean_embedded_video_link(form.cleaned_data['link'])
                if len(video.link) == 0:
                    form.errors['link'] = [u'Ссылка задана некорректно или данный тип ссылки не поддерживается.']
                    raise ValueError
                submitted_post_uid = form.cleaned_data['uid']
                if len(submitted_post_uid) > 0:
                    try:
                        other = VideoPost.objects.get(uid=submitted_post_uid)
                        if other.id != video.id:
                            form.errors['uid'] = [u'Заданный адрес уже используется другой новостью']
                            raise ValueError
                    except VideoPost.MultipleObjectsReturned:
                        # указанный адрес уже испольуется и где-то в базе есть конфликт адресов
                        form.errors[u'uid'] = u'Заданный адрес уже используется'
                        raise ValueError
                    except VideoPost.DoesNotExist:
                        pass

                    if not re.match('^[a-zA-Z0-9\-_]+$', submitted_post_uid):
                        form.errors['uid'] = [u'В адресе найдены запрещенные символы']
                        raise ValueError
                    video.uid = submitted_post_uid
                else:
                    form.errors[u'uid'] = u'Адрес не может быть пустым'
                    raise ValueError

                if form.cleaned_data['flag_del_preview']:
                    # stored preview file was deleted
                    if fs.exists(video.get_preview_path()):
                        fs.delete(video.get_preview_path())
                    video.preview_img = ""

                trash = []
                if len(form.cleaned_data['token_uid']) > 0 and request.session[form.cleaned_data['token_uid']] is not None:
                    # new preview file was submitted
                    f_info = request.session[form.cleaned_data['token_uid']]
                    del request.session[form.cleaned_data['token_uid']]
                    video.preview_img = f_info[1]
                    if fs.exists(f_info[0]):
                        f = fs.open(f_info[0])
                        fs.save(video.get_preview_path(), f)
                        f.close()
                        trash.append(f_info[0])
                video.save()
                for tfile in trash:
                    try:
                        fs.delete(tfile)
                    except IOError as err:
                        log.error("Failed to delete file '%s'. %s" % (tfile, err.message))
            else:
                raise ValueError
        except ValueError:
            response = render(request, 'management/video/edit.html',{
                'form' : form,
                'post' : video,
                'section' : 'video'
            })

    return response

@cache_control(must_revalidate=True)
def delete_article(request, id):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    response = None
    video = get_object_or_404(VideoPost, pk=id)
    if request.method == 'GET':
        result = render(request, "management/video/delete.html", {'post' : video, 'section' : 'video'})
    elif request.method == "POST":
        comments = VideoPostComment.objects.filter(video_post=video)
        for c in comments:
            c.delete()
        video.delete()
        result = redirect('management:video_index')
    else:
        result = redirect('management:news_index', permanent=True)

    return result

@never_cache
def attachment_upload(r):
    if not r.user.is_authenticated():
        return HttpResponse(get_script_response(code=403, message='Unauthorized'))

    if 'userfile' not in r.FILES:
        return HttpResponse(get_script_response(code=1, message='File expected'))

    f = r.FILES['userfile']     # file is present only if request method is POST and form type was specified
    log.debug("Upload file-type: %s" % f.content_type)
    if not f.content_type.startswith('image/'):
        return HttpResponse(get_script_response(code=1, message='File format not supported!'))

    obj_hash = "%s-%s-%s-%s" % (f.name, datetime.datetime.now().isoformat(' '), r.META['HTTP_USER_AGENT'], r.META['REMOTE_ADDR'])
    uid = hashlib.sha1(obj_hash.encode('utf-8')).hexdigest()
    #create new and unique filename
    ext = f.name.split('.')[-1]
    if len(ext) > 5:
        ext = ext[0:2]
    fname = "uploads/%s.%s" % (uid, ext)
    #save file in fs
    fs.save(fname, r.FILES['userfile'])
    #save link to uploaded file in session under unique key
    r.session[uid] = (fname, "%s.%s" % (uid, ext))
    #return link key and url to uploaded img
    return HttpResponse(get_script_response(code=0,message=uid,thumb_url=fs.url(fname)))

@never_cache
def attachment_remove(r):
    if not r.user.is_authenticated():
        return HttpResponse(get_json_response(code=403, message='Unauthorized'))
    log.info("processing request")
    try:
        if 'uid' in r.POST:
            log.info('uid is %s' % r.POST['uid'])
            fname_info = r.session[r.POST['uid']]
            fname = fname_info[0]
            if fname is None:
                raise ValueError('Upload id expired')
            if fs.exists(fname):
                del r.session[r.POST['uid']]
                try:
                    fs.delete(fname)
                except IOError as e:
                    log.error("Failed to delete file '%s'. %s" % (fname, e.message))
                    pass
        else:
            raise ValueError('Upload id is not correct')
    except ValueError as e:
        return HttpResponse(get_json_response(code=1, message=e.message))

    return HttpResponse(get_json_response(code=0))

def get_json_response(code, values = { } , message = ''):
    values['code'] = code
    values['message'] = message
    return json.dumps(values)

def get_script_response(code, message='', thumb_url=''):
    return '<script type="text/javascript">window.top.window.onUploadFinished(%s, "%s", "%s");</script>' %\
           (code, message, thumb_url)