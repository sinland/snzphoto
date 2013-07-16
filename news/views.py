from django.shortcuts import get_object_or_404, render
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

    return render(r, 'news/index.html', locals())

def show_post(r, post_uid):
    post = get_object_or_404(NewsPost, uid=post_uid)
    return render(r, 'news/post_details.html', locals())
