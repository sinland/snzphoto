# -*- coding: utf-8 -*-

import json
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from videos.models import *
from snzphoto import settings
from snzphoto.utils import get_json_response

#todo: видео: сделать капчу на добавление комментария

@never_cache
def index(r, page='1'):
    paginator = Paginator(VideoPost.objects.all().order_by('-creation_date', 'author'), settings.NEWS_PER_PAGE)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    section = "video"
    response = render(r, 'videos/index.html', locals())
    response.set_cookie('last_viewed_videospage', page)
    return response

@never_cache
def show_post(r, post_uid):
    section = "video"
    post = get_object_or_404(VideoPost, uid=post_uid)
    if 'last_viewed_videospage' in r.COOKIES:
        try:
            return_page = int(r.COOKIES['last_viewed_videospage'])
        except ValueError:
            return_page = 1
    if r.user.is_authenticated():
        comment_username = r.user
    elif 'comment_username' in r.COOKIES:
        comment_username = r.COOKIES['comment_username']
    else:
        comment_username = ""
    response = render(r, 'videos/post_details.html', locals())

    if 'last_viewed_newspage' in r.COOKIES:
        response.delete_cookie('last_viewed_videospage')
    return response

@never_cache
def get_comments(request, pid):
    respsonse = None
    try:
        post = VideoPost.objects.get(pk=pid)
        comments = VideoPostComment.objects.filter(video_post=post).order_by('creation_date', 'author_name')
        arr = list()
        for c in comments:
            arr.append(json.dumps(
                {
                    'author_name': c.author_name,
                    'msg': c.msg,
                    'cid': c.id
                    }
            ))

        respsonse = get_json_response(code=200, values={'comments' : arr})
    except VideoPost.DoesNotExist:
        respsonse = get_json_response(code=404, message='Post not found')
    return respsonse

@never_cache
def add_comment(request, pid):
    response = None
    if request.method != 'POST':
        response = get_json_response(code=405, message='Method not supported')
    else:
        try:
            post = VideoPost.objects.get(pk=pid)
            form = VideoCommentForm(request.POST)
            if not form.is_valid():
                response = get_json_response(code=400)
            else:
                comment = VideoPostComment(
                    video_post=post,
                    author_name=form.cleaned_data['author_name'],
                    msg=form.cleaned_data['msg']
                )
                comment.save()
                response = get_json_response(code=200)
        except VideoPost.DoesNotExist:
            response = get_json_response(code=404, message='Post not found')
    return response

@never_cache
def delete_comment(request, pid):
    if request.method != 'POST':
        response = get_json_response(code=400, message='Post please')
    else:
        if 'cid' not in request.POST:
            response = get_json_response(code=400, message='CID not found')
        else:
            cid = request.POST['cid']
            try:
                post = VideoPost.objects.get(pk=pid)
                if post.author.id != request.user.id:
                    response = get_json_response(code=403, message='Only post owners alowed')
                else:
                    comment = VideoPostComment.objects.get(pk=cid)
                    comment.delete()
                    response = get_json_response(code=200)
            except VideoPost.DoesNotExist:
                response = get_json_response(code=404, message='Post not found')
            except VideoPostComment.DoesNotExist:
                response = get_json_response(code=404, message='Comment not found')
    return response
