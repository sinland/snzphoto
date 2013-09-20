# -*- coding: utf-8 -*-
from types import NoneType

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django import forms
from snzphoto import settings
from snzphoto.utils import translit
from django.core.files.storage import default_storage as fs

class VideoPost(models.Model):
    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, db_column= 'author_id')
    title = models.CharField(max_length=256)
    text = models.TextField()
    link = models.CharField(max_length=1024)
    uid = models.CharField(max_length=256, unique=True)
    preview_img = models.CharField(max_length=128, default="")

    class Meta:
        db_table = "videoposts"

    def save(self, *args, **kwargs):
        if not self.id:
            tmp_uid = uniq_uid = translit(self.title)
            seed = 1
            while VideoPost.objects.filter(uid=uniq_uid).count() > 0:
                uniq_uid = "%s-%d" % (tmp_uid, seed)
                seed += 1
            self.uid = uniq_uid
        super(VideoPost, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('videos:show_post', kwargs={'post_uid' : self.uid})

    def comments_count(self):
        return VideoPostComment.objects.filter(video_post=self).count()

    def has_preview(self):
        if  str(self.preview_img) != "None":
            return len(self.preview_img) > 0
        else:
            return False

    """Путь к файлу изображения относительно корня хранилища"""
    def get_preview_path(self):
        if self.has_preview():
            return "videos_data/%s" % self.preview_img
        else:
            return "blank.png"

    """URL к файлу изображения относительно корня хранилища"""
    def get_preview_url(self):
        if self.has_preview():
            return fs.url(self.get_preview_path())
        else:
            return fs.url("blank.png")

class VideoPostComment(models.Model):
    class Meta:
        db_table = 'videocomments'

    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    video_post = models.ForeignKey(VideoPost, db_column= 'videopost_id')
    author_name = models.TextField(max_length=256)
    msg = models.TextField()

class VideoCommentForm(forms.Form):
    author_name = forms.CharField(max_length=256, label=u'Имя')
    msg = forms.CharField(label=u'Текст')
