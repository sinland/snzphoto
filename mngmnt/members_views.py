# -*- coding: utf-8 -*-
from django.views.decorators.cache import never_cache, cache_control
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from debates.models import DiscussionPost
from news.models import NewsPost
from models import MemberForm
from photos.models import PhotoAlbum
from videos.models import VideoPost

__author__ = 'PervinenkoVN'

def index(request, page=1):
    if not request.user.is_staff:
        return redirect('site_root')

    members = None
    paginator = Paginator(User.objects.all().order_by('-date_joined', 'username'), 20)
    try:
        members = paginator.page(page)
    except PageNotAnInteger:
        members = paginator.page(1)
    except EmptyPage:
        members = paginator.page(paginator.num_pages)

    return render(request, 'management/members/index.html', {
        'section' : 'members',
        'members' : members
    })

@never_cache
def edit(request, mid):
    if not request.user.is_staff:
        return redirect('site_root')

    response = None
    try:
        member = User.objects.get(pk=mid)
    except User.DoesNotExist:
        response = redirect('management:members_index')
        response['x-error-msg'] = '404: User not found'

    if member and request.method == 'GET':
        response = render(request, 'management/members/edit.html', {
            'section' : 'members',
            'member' : member,
            'form' : MemberForm(initial= {
                'first_name' : member.first_name,
                'last_name' : member.last_name,
                'email' : member.email,
                'is_active' : member.is_active,
                'is_staff' : member.is_staff
            })
        })
    elif member and request.method == 'POST':
        form = MemberForm(request.POST)
        if not form.is_valid():
            response = render(request, 'management/members/edit.html', {
                'section' : 'members',
                'form' : form
            })
        else:
            member.first_name = form.cleaned_data['first_name']
            member.last_name = form.cleaned_data['last_name']
            member.email = form.cleaned_data['email']
            member.is_active = form.cleaned_data['is_active']
            member.is_staff = form.cleaned_data['is_staff']
            member.save()
            response = redirect('management:members_index')
    else:
        response = redirect('management:members_index')
        response['x-error-msg'] = '500 Method is not supported'
    return response


def add(request):
    if not request.user.is_staff:
        return redirect('site_root')

    response = None
    if request.method == 'GET':
        response = render(request, 'management/members/add.html', {
            'section' : 'members',
            'form' : MemberForm()
        })
    elif request.method == 'POST':
        form = MemberForm(request.POST)
        if not form.is_valid():
            response = render(request, 'management/members/add.html', {
                'section' : 'members',
                'form' : form
            })
        elif len(form.cleaned_data['password']) == 0:
            form.errors['password'] = [u'Пароль не должен быть пустым']
            response = render(request, 'management/members/add.html', {
                'section' : 'members',
                'form' : form
            })
        else:
            member = User.objects.create_user(
                username=form.cleaned_data['login'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            member.first_name = form.cleaned_data['first_name']
            member.last_name = form.cleaned_data['last_name']
            member.is_active = form.cleaned_data['is_active']
            member.is_staff = form.cleaned_data['is_staff']
            member.save()

            response = redirect('management:members_index')
    else:
        response = redirect('management:members_index')
        response['x-error-msg'] = '500 Method is not supported'
    return response


def delete(request, mid):
    if not request.user.is_staff:
        return redirect('site_root')

    response = None
    member = None

    try:
        member = User.objects.get(pk=mid)
    except User.DoesNotExist:
        response = redirect('management:members_index')
        response['x-error-msg'] = '404: User not found'

    if member and request.method == 'GET':
        response = render(request, 'management/members/delete.html', {
            'section' : 'members',
            'member' : member
        })
    elif member and request.method == 'POST':
        if NewsPost.objects.filter(author=member).count() > 0:
            response = render(request, 'management/members/delete.html', {
                'section' : 'members',
                'member' : member,
                'error' : u'Невозможно удалить пользователя: удалите записи в разделе "Новости" созданные этим пользоватем!'
            })
        elif PhotoAlbum.objects.filter(author=member).count() > 0:
            response = render(request, 'management/members/delete.html', {
                'section' : 'members',
                'member' : member,
                'error' : u'Невозможно удалить пользователя: удалите записи в разделе "Галерея" созданные этим пользоватем!'
            })
        elif VideoPost.objects.filter(author=member).count() > 0:
            response = render(request, 'management/members/delete.html', {
                'section' : 'members',
                'member' : member,
                'error' : u'Невозможно удалить пользователя: удалите записи в разделе "Видео" созданные этим пользоватем!'
            })
        elif DiscussionPost.objects.filter(author=member).count() > 0:
            response = render(request, 'management/members/delete.html', {
                'section' : 'members',
                'member' : member,
                'error' : u'Невозможно удалить пользователя: удалите записи в разделе "Обсуждения" созданные этим пользоватем!'
            })
        else:
            member.delete()
            response = redirect('management:members_index')
    else:
        response = redirect('management:members_index')
        response['x-error-msg'] = '500 Method is not supported'
    return response