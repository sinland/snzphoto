# -*- coding: utf-8 -*-
import random
from django.contrib.auth.models import User
from django.core.files.storage import default_storage as fs
from django.core.urlresolvers import reverse
from django.db import models
from snzphoto.utils import translit

class PhotoAlbum(models.Model):
    class Meta:
        db_table = "photoalbums"

    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, db_column='author_id')
    title = models.CharField(max_length=256)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    views_counter = models.BigIntegerField()

    cached_photos = []

    def photos_count(self):
        return Photo.objects.filter(album=self).count()

    def get_photos(self):
        if len(self.cached_photos) == 0:
            self.cached_photos = Photo.objects.filter(album=self)
        return self.cached_photos

    def get_random_photo_url(self):
        total = self.photos_count()
        photo = fs.url('gallery/blank.png')
        if total > 0:
            indx = random.randint(0, self.photos_count() - 1)
            photo = self.get_photos()[indx].get_thumb_url()
        return photo

    def get_random_pics_url(self):
        pics_count = 1
        total = self.photos_count()
        if total == 0:
            return []
        if total < pics_count:
            pics_count = total

        result = []
        for i in range(pics_count):
            for j in range(total):
                indx = random.randint(0, total - 1)
                pic = self.get_photos()[indx].get_thumb_url()
                try:
                    result.index(pic)
                except ValueError:
                    result.append(pic)
                    break
        return result

    def get_absolute_url(self):
        return reverse('news:show_post', kwargs={'post_uid' : self.uid})

class Photo(models.Model):
    class Meta:
        db_table='photos'

    id = models.AutoField(primary_key=True)
    album = models.ForeignKey(PhotoAlbum, db_column='photoalbum_id')
    creation_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    filename = models.CharField(max_length=128)
    thumbfile = models.CharField(max_length=128)
    author = models.CharField(max_length=512)
    likes_count = models.BigIntegerField()

    """Путь к файлу изображения относительно корня хранилища"""
    def get_file_path(self):
        return "gallery/%d/%s" % (self.album.id, self.filename)

    """Путь к файлу эскиза изображения относительно корня хранилища"""
    def get_thumb_path(self):
        return "gallery/%d/thumbs/%s" % (self.album.id, self.thumbfile)

    """URL к файлу изображения относительно корня хранилища"""
    def get_file_url(self):
        return fs.url(self.get_file_path())

    """URL к файлу эскиза изображения относительно корня хранилища"""
    def get_thumb_url(self):
        return fs.url(self.get_thumb_path())