# -*- coding: utf-8 -*-

import json
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.views.decorators.cache import never_cache
from debates.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from snzphoto import settings
from snzphoto.utils import get_json_response

#todo: новости: сделать капчу на добавление комментария

@never_cache
def index(r, page='1'):
    paginator = Paginator(DiscussionPost.objects.all().order_by('-creation_date', 'author'), settings.NEWS_PER_PAGE)
    try:
        view_news = paginator.page(page)
    except PageNotAnInteger:
        view_news = paginator.page(1)
    except EmptyPage:
        view_news = paginator.page(paginator.num_pages)

    section = 'debates'
    response = render(r, 'debates/index.html', locals())
    response.set_cookie('last_viewed_forumpage', page)
    return response

@never_cache
def details(r, id):
    section = 'news'
    post = get_object_or_404(DiscussionPost, pk=id)
    if 'last_viewed_forumpage' in r.COOKIES:
        try:
            return_page = int(r.COOKIES['last_viewed_forumpage'])
        except ValueError:
            return_page = 1
    if r.user.is_authenticated():
        comment_username = r.user
    elif 'comment_username' in r.COOKIES:
        comment_username = r.COOKIES['comment_username']
    else:
        comment_username = ""
    response = render(r, 'debates/post_details.html', locals())
    if 'last_viewed_forumpage' in r.COOKIES:
        response.delete_cookie('last_viewed_forumpage')
    return response

@never_cache
def get_comments(request, pid):
    respsonse = None
    try:
        post = DiscussionPost.objects.get(pk=pid)
        comments = DiscussionPostComment.objects.filter(news_post=post).order_by('creation_date', 'author_name')
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
    except DiscussionPost.DoesNotExist:
        respsonse = get_json_response(code=404, message='Post not found')
    return respsonse

@never_cache
def add_comment(request, pid):
    response = None
    if request.method != 'POST':
        response = get_json_response(code=405, message='Method not supported')
    else:
        try:
            post = DiscussionPost.objects.get(pk=pid)
            form = DiscussionPostCommentForm(request.POST)
            if not form.is_valid():
                response = get_json_response(code=400)
            else:
                comment = DiscussionPostComment(
                    post=post,
                    author_name=escape(form.cleaned_data['author_name']),
                    msg=form.cleaned_data['msg']
                )
                comment.save()
                response = get_json_response(code=200, values={'cid' : comment.id})
                try:
                    response.set_cookie('comment_username', comment.author_name)
                except ValueError:
                    pass
        except DiscussionPost.DoesNotExist:
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
                post = DiscussionPost.objects.get(pk=pid)
                if post.author.id != request.user.id:
                    response = get_json_response(code=403, message='Only post owners allowed')
                else:
                    comment = DiscussionPostComment.objects.get(pk=cid)
                    comment.delete()
                    response = get_json_response(code=200)
            except DiscussionPost.DoesNotExist:
                response = get_json_response(code=404, message='Post not found')
            except DiscussionPostComment.DoesNotExist:
                response = get_json_response(code=404, message='Comment not found')
    return response
