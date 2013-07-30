# -*- coding: utf-8 -*-

import re
import json
import logging
import hashlib
import datetime
from PIL import Image
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache, cache_control
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage as fs
from news.models import *
from mngmnt.models import *

#global objects
log = logging.getLogger(name='manager.ajax')

@cache_control(must_revalidate=True)
def index(request, page = 1):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    paginator = Paginator(NewsPost.objects.all().order_by('-creation_date', 'author'), 20)
    try:
        view_news = paginator.page(page)
    except PageNotAnInteger:
        view_news = paginator.page(1)
    except EmptyPage:
        view_news = paginator.page(paginator.num_pages)

    return render(request, 'management/news/index.html', {
        'news' : view_news,
        'section' : 'news',
        'total_count' : NewsPost.objects.count()
    })

@never_cache
def add_article(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    result = None
    if request.method == 'GET':
        result = render(request, 'management/news/add.html',{
            'form' : NewsPostForm(),
            'section' : 'news'
        })
    elif request.method == 'POST':
        form = NewsPostForm(request.POST)
        tmp_attach_name = uploaded_file = uploaded_thumb_file = thumb_url = None
        if 'tmp_attach_name' in request.POST and len(request.POST['tmp_attach_name']) > 0:
            if re.match('[a-z0-9]+\.[a-z]+', request.POST['tmp_attach_name']):
                tmp_attach_name = request.POST['tmp_attach_name']
                uploaded_thumb_file = "uploads/%s" % NewsPost.get_thumbname_from_base(tmp_attach_name)
                uploaded_file = 'uploads/%s' % tmp_attach_name
                if fs.exists(uploaded_thumb_file):
                    thumb_url = fs.url(uploaded_thumb_file)

        if not form.is_valid():
            result = render(request, 'management/news/add.html',{
                'form' : form,
                'section' : 'news',
                'tmp_attach_name' : tmp_attach_name,
                'tmp_thumb_url' : thumb_url
            })
        else:
            news_obj = NewsPost(
                author=request.user,
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text']
            )

            trash = list()
            if tmp_attach_name:
                new_stored_file = 'news/%s' % tmp_attach_name
                new_stored_thumb_file = "news/thumbs/%s" % NewsPost.get_thumbname_from_base(tmp_attach_name)

                if fs.exists(uploaded_file):
                    # переместим сам файл из uploads на его место
                    f = fs.open(uploaded_file)
                    fs.save(new_stored_file, f)
                    f.close()
                    trash.append(uploaded_file)

                    #переместим файл эскиза из uploads на его место
                    if fs.exists(uploaded_thumb_file):
                        f = fs.open(uploaded_thumb_file)
                        fs.save(new_stored_thumb_file, f)
                        f.close()
                        trash.append(uploaded_thumb_file)

                    #сохраним инфо в БД
                    news_obj.enclosure = tmp_attach_name

            news_obj.save()
            result = redirect('management:news_index')
            result['X-Operation-Status'] = 'success'
            for tfile in trash:
                if fs.exists(tfile):
                    try:
                        fs.delete(tfile)
                    except:
                        pass
    return result

@never_cache
def edit_article(request, news_id):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    try:
        news_obj = NewsPost.objects.get(pk=news_id)
    except NewsPost.DoesNotExist:
        return redirect('management:news_index', permanent=True)

    if request.method == 'GET':
        return render(request, 'management/news/edit.html',{
            'form' : NewsPostForm(initial={
                'title' : news_obj.title,
                'text' : news_obj.text,
                'uid' : news_obj.uid
            }),
            'post' : news_obj,
            'section' : 'news'
        })
    elif request.method == 'POST':
        form = NewsPostForm(request.POST)
        try:
            if form.is_valid():
                news_obj.title = form.cleaned_data['title']
                news_obj.text = form.cleaned_data['text']
                token_uid = form.cleaned_data['uid']
                if len(token_uid) > 0:
                    try:
                        post = NewsPost.objects.get(uid=token_uid)
                        if post.id != news_obj.id:
                            form.errors['uid'] = [u'Заданный адрес уже используется другой новостью']
                            raise ValueError
                    except NewsPost.MultipleObjectsReturned:
                        # указанный адрес уже испольуется и где-то в базе есть конфликт адресов
                        form.errors[u'uid'] = u'Заданный адрес уже используется'
                        raise ValueError
                    except NewsPost.DoesNotExist:
                        pass

                    if not re.match('^[a-zA-Z0-9\-_]+$', token_uid):
                        form.errors['uid'] = [u'В адресе найдены запрещенные символы']
                        raise ValueError
                    news_obj.uid = token_uid

                trash = list()
                if 'flag_rm_attach' in request.POST and len(request.POST['flag_rm_attach']) > 0:
                    trash.append('news/%s' % news_obj.enclosure)
                    trash.append("news/thumbs/%s" % news_obj.get_thumbfile_name())
                    news_obj.enclosure = ""

                if 'tmp_attach_name' in request.POST and len(request.POST['tmp_attach_name']) > 0:
                    if not re.match('[a-z0-9]+\.[a-z]+', request.POST['tmp_attach_name']):
                        form.errors[u'uid'] = u'Ошибка загрузки файла. Презагрузите страницу и повторите операцию'
                        raise ValueError

                    fname_base = request.POST['tmp_attach_name']
                    uploaded_file = 'uploads/%s' % fname_base
                    new_stored_file = 'news/%s' % fname_base
                    uploaded_thumb_file = "uploads/%s" % NewsPost.get_thumbname_from_base(fname_base)
                    new_stored_thumb_file = "news/thumbs/%s" % NewsPost.get_thumbname_from_base(fname_base)

                    # если загруженный файл есть в приватном хранилище
                    if fs.exists(uploaded_file):
                        news_obj.enclosure = fname_base

                        # переместим его в публичное
                        f = fs.open(uploaded_file)
                        fs.save(new_stored_file, f)
                        f.close()
                        trash.append(uploaded_file)

                        #переместим файл эскиза из uploads на его место
                        if fs.exists(uploaded_thumb_file):
                            f = fs.open(uploaded_thumb_file)
                            fs.save(new_stored_thumb_file, f)
                            f.close()
                            trash.append(uploaded_thumb_file)

                news_obj.save()

                for tfile in trash:
                    if fs.exists(tfile):
                        try:
                            fs.delete(tfile)
                        except:
                            pass
            else:
                raise ValueError
        except ValueError:
            return render(request, 'management/news/edit.html',{
                'form' : form,
                'post' : news_obj,
                'section' : 'news'
            })

    resp = redirect('management:news_index')
    resp['X-Operation-Status'] = 'success'
    return resp

@never_cache
def delete_article(request, news_id):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(render_to_string('forbidden.html', context_instance=RequestContext(request)))

    result = None
    try:
        news_obj = NewsPost.objects.get(pk=news_id)
        if request.method == 'GET':
            result = render(request, "management/news/delete.html", {'post' : news_obj, 'section' : 'news'})
            result["X-RCode"] = 200
        elif request.method == "POST":
            comments = NewsPostComment.objects.filter(news_post=news_obj)
            for c in comments:
                c.delete()
            trash = list()
            if len(news_obj.enclosure) > 0:
                trash.append('news/%s' % news_obj.enclosure)
                trash.append("news/thumbs/%s" % news_obj.get_thumbfile_name())

            news_obj.delete()
            for tfile in trash:
                if fs.exists(tfile):
                    try:
                        fs.delete(tfile)
                    except:
                        pass
            result = redirect('management:news_index', kwargs = {'msg' : 'Hello World!!!'})
            result["X-RCode"] = 200
        else:
            result = redirect('management:news_index', permanent=True)
            result["X-RCode"] = "500: Invalid method"
    except NewsPost.DoesNotExist:
        result = redirect('management:news_index', permanent=True)
        result["X-RCode"] = 404
    except Exception as ex:
        result = redirect('management:news_index', permanent=True)
        result["X-RCode"] = "500: %s" % ex.message

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

    hash_base = "%s-%s-%s" % (f.name, datetime.datetime.now().isoformat(' '), r.META['HTTP_USER_AGENT'])
    fname_base = hashlib.sha1(hash_base).hexdigest()
    ext = f.name.split('.')[-1]
    if len(ext) > 5:
        ext = ext[0:2]
    fname_base = "%s.%s" % (fname_base, ext)
    thumb_file = 'uploads/%s' % NewsPost.get_thumbname_from_base(fname_base)

    log.debug("Generated name for upload: %s" % fname_base)
    log.debug("Generated filename for thumbnail: %s" % thumb_file)

    fs.save('uploads/%s' % fname_base, r.FILES['userfile'])

    try:
        im = Image.open(fs.path('uploads/%s' % fname_base))
        im.thumbnail(settings.IMG_THUMBS_SIZE, Image.ANTIALIAS)
        im.save(fs.path(thumb_file), "JPEG")
    except Exception:
        fs.save(thumb_file, r.FILES['userfile'])

    #return url to it
    return HttpResponse(
        get_script_response(code=0,
            message=fname_base,
            thumb_url=fs.url(thumb_file)
        )
    )

@never_cache
def attachment_remove(r):
    if not r.user.is_authenticated():
        return HttpResponse(get_json_response(code=403, message='Unauthorized'))

    try:
        if 'base_name' in r.POST and len(r.POST['base_name']) > 0:
            # deleting recently uploaded image
            if not re.match('[a-z0-9]+\.[a-z]+', r.POST['base_name']):
                raise ValueError(u'Передано некорректное имя файла')

            fname_base = r.POST['base_name']
            uploaded_file = 'uploads/%s' % fname_base
            thumb_file = "uploads/%s" % NewsPost.get_thumbname_from_base(fname_base)
            if fs.exists(uploaded_file):
                try:
                    fs.delete(uploaded_file)
                except:
                    pass
            if fs.exists(thumb_file):
                try:
                    fs.delete(thumb_file)
                except:
                    pass
    except ValueError as e:
        HttpResponse(get_json_response(code=1, message=e.message))

    return HttpResponse(get_json_response(code=0))

def get_json_response(code, values = {} , message = ''):
    values['code'] = code
    values['message'] = message
    return json.dumps(values)

def get_script_response(code, message='', thumb_url=''):
    return '<script type="text/javascript">window.top.window.onUploadFinished(%s, "%s", "%s");</script>' %\
           (code, message, thumb_url)

