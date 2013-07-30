# -*- coding: utf-8 -*-
import re
from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from snzphoto.utils import clean_embedded_video_link

__author__ = 'PervinenkoVN'

from django.views.decorators.cache import never_cache, cache_control
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from videos.models import *
from mngmnt.models import *

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
                post.save()
                result = redirect('management:video_index')
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
            'section' : 'video'
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
                token_uid = form.cleaned_data['uid']
                if len(token_uid) > 0:
                    try:
                        other = VideoPost.objects.get(uid=token_uid)
                        if other.id != video.id:
                            form.errors['uid'] = [u'Заданный адрес уже используется другой новостью']
                            raise ValueError
                    except VideoPost.MultipleObjectsReturned:
                        # указанный адрес уже испольуется и где-то в базе есть конфликт адресов
                        form.errors[u'uid'] = u'Заданный адрес уже используется'
                        raise ValueError
                    except VideoPost.DoesNotExist:
                        pass

                    if not re.match('^[a-zA-Z0-9\-_]+$', token_uid):
                        form.errors['uid'] = [u'В адресе найдены запрещенные символы']
                        raise ValueError
                    video.uid = token_uid
                else:
                    form.errors[u'uid'] = u'Адрес не может быть пустым'
                    raise ValueError

                video.save()
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