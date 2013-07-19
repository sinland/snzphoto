# -*- coding: utf-8 -*-
from django.views.decorators.cache import never_cache, cache_control
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from models import MemberForm

__author__ = 'PervinenkoVN'

def index(request, page=1):
    if not request.user.is_staff:
        return redirect('news:index')

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
        return redirect('news:index')

    response = None
    try:
        member = User.objects.get(pk=mid)
    except User.DoesNotExist:
        response = redirect('management:members_index')
        response['x-error-msg'] = '404: User not found'
    if request.method == 'GET':
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
    elif request.method == 'POST':
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
        return redirect('news:index')

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