from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from news.models import *
from mngmnt.models import *
#from django.contrib.auth.decorators import login_required
# Create your views here.

#@login_required(redirect_field_name='goto', login_url= reverse('news:index'))
from snzphoto import settings

def index(r):
    if not r.user.is_authenticated():
        return redirect('news:index')
    return render(r, 'management/index.html', {})

def news_index(r, page = 1):
    if not r.user.is_authenticated():
        return redirect('news:index')

    paginator = Paginator(NewsPost.objects.all(), 10)
    try:
        view_news = paginator.page(page)
    except PageNotAnInteger:
        view_news = paginator.page(1)
    except EmptyPage:
        view_news = paginator.page(paginator.num_pages)

    return render(r, 'management/news_index.html', {'news' : view_news})

def news_add(r):
    if not r.user.is_authenticated():
        return redirect('news:index')
    return None

def news_edit(r, news_id):
    if not r.user.is_authenticated():
        return redirect('news:index', permanent=True)

    try:
        news_obj = NewsPost.objects.get(pk=news_id)
    except NewsPost.DoesNotExist:
        return redirect('management:news_index', permanent=True)

    if r.method == 'GET':
        return render(r, 'management/news_edit.html', {'form' : NewsPostForm(instance=news_obj)})
    elif r.method == 'POST':
        form = NewsPostForm(r.POST, instance=news_obj)
        if form.is_valid():
            form.save()

    #return to index
    return redirect('management:news_index')

def news_delete(r, news_id):
    if not r.user.is_authenticated():
        return redirect('news:index')

    return None