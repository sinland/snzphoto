# -*- coding: utf-8 -*-

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from news.models import *
from mngmnt.models import *

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

    return render(r, 'management/news_index.html', {'news' : view_news, 'section' : 'news'})

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
        return render(r, 'management/news_edit.html',{
                'form' : NewsPostForm(initial={
                    'title' : news_obj.title,
                    'text' : news_obj.text,
                    'uid' : news_obj.uid
                }),
                'post' : news_obj,
                'section' : 'news'
        })
    elif r.method == 'POST':
        form = NewsPostForm(r.POST)
        try:
            if form.is_valid():
                news_obj.title = form.cleaned_data['title']
                news_obj.text = form.cleaned_data['text']
                token_uid = form.cleaned_data['uid']
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

                news_obj.uid = token_uid
                news_obj.save()
            else:
                raise ValueError
        except ValueError:
            return render(r, 'management/news_edit.html',{
                'form' : form,
                'post' : news_obj,
                'section' : 'news'
            })

    #return to index
    return redirect('management:news_index')

def news_delete(r, news_id):
    if not r.user.is_authenticated():
        return redirect('news:index')

    return None


