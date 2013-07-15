from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response, get_object_or_404
from news.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from snzphoto import settings

# Create your views here.
def index(r, page='1'):
    paginator = Paginator(NewsPost.objects.all(), settings.NEWS_PER_PAGE)
    try:
        view_news = paginator.page(page)
    except PageNotAnInteger:
        view_news = paginator.page(1)
    except EmptyPage:
        view_news = paginator.page(paginator.num_pages)

    return render_to_response('news/index.html', locals())

def show_post(r, post_uid):
    post = get_object_or_404(NewsPost, uid=post_uid)
    return render_to_response('news/post_details.html', locals())
