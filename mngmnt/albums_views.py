# -*- coding: utf-8 -*-

import re
import json
import logging
import hashlib
import datetime
from PIL import Image
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage as fs
from mngmnt.models import *

def index(request):
    return render(request, 'management/albums/index.html', {'section' : 'albums'})