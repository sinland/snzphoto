from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

__author__ = 'PervinenkoVN'
from django.http import HttpResponse

def logout_action(r):
    logout(r)
    return HttpResponseRedirect(reverse('news:index'))



