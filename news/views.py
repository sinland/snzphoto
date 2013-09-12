# -*- coding: utf-8 -*-

import json
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.views.decorators.cache import never_cache
from news.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from recaptcha.client import captcha
from snzphoto import settings
from snzphoto.utils import get_json_response

#todo: новости: сделать капчу на добавление комментария

@never_cache
def index(r, page='1'):
    paginator = Paginator(NewsPost.objects.all().order_by('-creation_date', 'author'), settings.NEWS_PER_PAGE)
    try:
        view_news = paginator.page(page)
    except PageNotAnInteger:
        view_news = paginator.page(1)
    except EmptyPage:
        view_news = paginator.page(paginator.num_pages)

    section = 'news'

    if view_news.number - 1 > 2:
        first_page = 1 # первая страница стоит отдельно
    if paginator.num_pages - view_news.number > 2:
        last_page = paginator.num_pages # последняя страница стоит отдельно
    pages_range = paginator.page_range[view_news.number:view_news.number+3]
    left_range = view_news.number-3
    if left_range < 0:
        left_range = 0
    for p in paginator.page_range[left_range:view_news.number]:
        pages_range.append(p)
    pages_range.sort()
    response = render(r, 'news/index.html', locals())
    response.set_cookie('last_viewed_newspage', page)
    return response

@never_cache
def show_post(r, post_uid):
    section = 'news'
    post = get_object_or_404(NewsPost, uid=post_uid)
    if 'last_viewed_newspage' in r.COOKIES:
        try:
            return_page = int(r.COOKIES['last_viewed_newspage'])
        except ValueError:
            return_page = 1
    else:
        return_page = 1
    if r.user.is_authenticated():
        comment_username = r.user
    elif 'comment_username' in r.COOKIES:
        comment_username = r.COOKIES['comment_username']
    else:
        comment_username = ""
    response = render(r, 'news/post_details.html', locals())
#    if 'last_viewed_newspage' in r.COOKIES:
#        response.delete_cookie('last_viewed_newspage')
    return response

@never_cache
def get_comments(request, pid):
    respsonse = None
    try:
        post = NewsPost.objects.get(pk=pid)
        comments = NewsPostComment.objects.filter(news_post=post).order_by('creation_date', 'author_name')
        arr = list()
        for c in comments:
            arr.append(json.dumps(
                {
                    'author_name': c.author_name,
                    'msg': c.msg,
                    'cid': c.id,
                    'date': c.creation_date.strftime("%d.%m.%Y %H:%M")
                    }
            ))
        respsonse = get_json_response(code=200, values={'comments' : arr})
    except NewsPost.DoesNotExist:
        respsonse = get_json_response(code=404, message='Post not found')
    return respsonse

@never_cache
def add_comment(request, pid):
    response = None
    if request.method != 'POST':
        return get_json_response(code=405, message='Method not supported')
    try:
        post = NewsPost.objects.get(pk=pid)
        if 'challenge' not in request.POST or 'response' not in request.POST:
            raise ValueError('Captcha validation failed: response missing')
        captcha_response = captcha.submit(
            request.POST['challenge'],
            request.POST['response'],
            settings.RECAPCHA_PRIVATE_API_KEY,
            request.META['REMOTE_ADDR']
        )
        if not captcha_response.is_valid:
            raise ValueError('Captcha validation failed')

        form = NewsCommentForm(request.POST)
        if not form.is_valid():
            raise ValueError('Comment format invalid')

        comment = NewsPostComment(
            news_post=post,
            author_name=escape(form.cleaned_data['author_name']),
            msg=form.cleaned_data['msg']
        )
        comment.save()
        response = get_json_response(code=200, values={'cid' : comment.id, 'date':comment.creation_date.strftime("%d.%m.%Y %H:%M") })
        try:
            response.set_cookie('comment_username', comment.author_name)
        except ValueError:
            pass
    except NewsPost.DoesNotExist:
        response = get_json_response(code=404, message='Post not found')
    except ValueError as e:
        response = get_json_response(code=400, message=e.message)
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
                post = NewsPost.objects.get(pk=pid)
                if post.author.id != request.user.id:
                    response = get_json_response(code=403, message='Only post owners alowed')
                else:
                    comment = NewsPostComment.objects.get(pk=cid)
                    comment.delete()
                    response = get_json_response(code=200)
            except NewsPost.DoesNotExist:
                response = get_json_response(code=404, message='Post not found')
            except NewsPostComment.DoesNotExist:
                response = get_json_response(code=404, message='Comment not found')
    return response
