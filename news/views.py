import json
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from news.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from snzphoto import settings
from snzphoto.utils import get_json_response

@never_cache
def index(r, page='1'):
    paginator = Paginator(NewsPost.objects.all().order_by('-creation_date', 'author'), settings.NEWS_PER_PAGE)
    try:
        view_news = paginator.page(page)
    except PageNotAnInteger:
        view_news = paginator.page(1)
    except EmptyPage:
        view_news = paginator.page(paginator.num_pages)

    response = render(r, 'news/index.html', locals())
    response.set_cookie('last_viewed_newspage', page)
    return response

@never_cache
def show_post(r, post_uid):
    post = get_object_or_404(NewsPost, uid=post_uid)
    if 'last_viewed_newspage' in r.COOKIES:
        try:
            return_page = int(r.COOKIES['last_viewed_newspage'])
        except ValueError:
            pass
    response = render(r, 'news/post_details.html', locals())
    if 'last_viewed_newspage' in r.COOKIES:
        response.delete_cookie('last_viewed_newspage')
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
        response = get_json_response(code=405, message='Method not supported')
    else:
        try:
            post = NewsPost.objects.get(pk=pid)
            form = NewsCommentForm(request.POST)
            if not form.is_valid():
                response = get_json_response(code=400)
            else:
                comment = NewsPostComment(news_post=post,
                    author_name=form.cleaned_data['author_name'],
                    msg=form.cleaned_data['msg']
                )
                comment.save()
                response = get_json_response(code=200)
        except NewsPost.DoesNotExist:
            response = get_json_response(code=404, message='Post not found')
    return response

@never_cache
def delete_comment(request, pid):
    return None
