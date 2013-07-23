from django.contrib.auth.models import User
from django.db import models

class PhotoAlbum(models.Model):
    class Meta:
        db_table = "photoalbums"

    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, db_column='author_id')
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=2048)
    creation_date = models.DateTimeField(auto_now_add=True)
    views_counter = models.BigIntegerField()

    def photos_count(self):
        return Photo.objects.filter(album=self).count()

    def get_photos(self):
        return Photo.objects.filter(album=self)

class Photo(models.Model):
    class Meta:
        db_table='photos'

    id = models.AutoField(primary_key=True)
    album = models.ForeignKey(PhotoAlbum, db_column='photoalbum_id')
    creation_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=4*1024)
    filename = models.CharField(max_length=128)
    thumbfile = models.CharField(max_length=128)
    author = models.CharField(max_length=512)
    likes_count = models.BigIntegerField()

    def get_file_path(self):
        return "gallery/%d/%s" % (self.album.id, self.filename)

    def get_thumb_path(self):
        return "gallery/%d/thumbs/%s" % (self.album.id, self.thumbfile)