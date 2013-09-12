# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django import forms
from snzphoto import settings
from snzphoto.utils import translit

class NewsPost(models.Model):
    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, db_column= 'author_id')
    title = models.CharField(max_length=256)
    text = models.TextField()
    enclosure = models.CharField(max_length=256, blank=True)
    uid = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = "newsposts"

    def save(self, *args, **kwargs):
        if not self.id:
            tmp_uid = uniq_uid = translit(self.title)
            seed = 1
            while NewsPost.objects.filter(uid=uniq_uid).count() > 0:
                uniq_uid = "%s-%d" % (tmp_uid, seed)
                seed += 1
            self.uid = uniq_uid
        super(NewsPost, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:show_post', kwargs={'post_uid' : self.uid})

    def attach_thumb_url(self):
        return "%snews/thumbs/%s" % (settings.MEDIA_URL, NewsPost.get_thumbname_from_base(self.enclosure))

    def attach_full_url(self):
        return "%snews/%s" % (settings.MEDIA_URL, self.enclosure)

    def get_thumbfile_name(self):
        return NewsPost.get_thumbname_from_base(self.enclosure)

    def comments_count(self):
        return NewsPostComment.objects.filter(news_post=self).count()

    @staticmethod
    def get_thumbname_from_base(base):
        return "thumb_%s" % base

class NewsPostComment(models.Model):
    class Meta:
        db_table = 'newscomments'

    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    news_post = models.ForeignKey(NewsPost, db_column= 'newspost_id')
    author_name = models.TextField(max_length=256)
    msg = models.TextField()

class NewsCommentForm(forms.Form):
    author_name = forms.CharField(max_length=256, label=u'Имя')
    msg = forms.CharField(label=u'Текст')
