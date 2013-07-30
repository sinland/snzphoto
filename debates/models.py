# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django import forms
from django.core.files.storage import default_storage as fs


class DiscussionPost(models.Model):
    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, db_column= 'author_id')
    title = models.CharField(max_length=256)
    text = models.TextField()
    attach = models.CharField(max_length=256, blank=True)
    attach_thumb = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = "discussions"

    def attach_thumb_url(self):
        return fs.url(self.attach_thumb_path())

    def attach_url(self):
        return  fs.url(self.attach_path())

    def attach_thumb_path(self):
        return "discussions/thumbs/%s" % self.attach_thumb

    def attach_path(self):
        return 'discussions/%s' % self.attach

    def comments_count(self):
        return DiscussionPostComment.objects.filter(post=self).count()

    def get_comments(self):
        return DiscussionPostComment.objects.filter(post=self)

class DiscussionPostComment(models.Model):
    class Meta:
        db_table = 'discuss_comments'

    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(DiscussionPost, db_column= 'post_id')
    author_name = models.TextField(max_length=256)
    msg = models.TextField()

class DiscussionPostCommentForm(forms.Form):
    author_name = forms.CharField(max_length=256, label=u'Имя')
    msg = forms.CharField(label=u'Текст')
