from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from snzphoto.utils import translit

class NewsPost(models.Model):
    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, db_column= 'author_id')
    title = models.CharField(max_length=256)
    text = models.TextField()
    enclosure = models.CharField(max_length=256, blank=True)
    uid = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "newsposts"

    def save(self, *args, **kwargs):
        if not self.id:
            tmp_uid = translit(self.title)
            similar = NewsPost.objects.filter(uid=tmp_uid)
            if similar.count() > 0:
                tmp_uid = "%s-%d" % (tmp_uid, similar.count() + 1)
            self.uid = tmp_uid
        super(NewsPost, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:show_post', kwargs={'post_uid' : self.uid})

class NewsPostComment(models.Model):
    class Meta:
        db_table = 'newscomments'

    id = models.AutoField(primary_key=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    news_post = models.ForeignKey(NewsPost, db_column= 'newspost_id')
    author = models.ForeignKey(User, db_column= 'author_id')
    text = models.TextField()



