__author__ = 'PervinenkoVN'
import json
from django.http import HttpResponse
from django.core.files.storage import default_storage
import hashlib
import datetime
import logging

log = logging.getLogger(name='manager.ajax')

def news_picture_upload_handler(r, news_id):
    if 'userfile' not in r.FILES:
        return HttpResponse(get_script_response(code=1, message='File missed!'))

    f = r.FILES['userfile']
    if not f.content_type.startswith('image/'):
        return HttpResponse(get_script_response(code=1, message='File format not supported!'))

    hash_base = "%s-%s-%s" % (f.name, datetime.datetime.now().isoformat(' '), r.META['HTTP_USER_AGENT'])
    stored_name = hashlib.sha1(hash_base).hexdigest()
    ext = f.name.split('.')[-1]
    if len(ext) > 5:
        ext = ext[0:2]
    stored_name = "%s.%s" % (stored_name, ext)

    log.debug("Generated name: %s" % stored_name)
    log.debug("file-type: %s" % f.content_type)

#    default_storage.save('tmp/%s' % stored_name, r.FILES['userfile'])
    return HttpResponse(get_script_response(code=0, message='success', thumb_name=stored_name));

def get_json_response(code, values = {} , message = ''):
    values['code'] = code
    values['message'] = message
    return json.dumps(values)

def get_script_response(code, message='', thumb_name=''):
    return '<script type="text/javascript">window.top.window.onUploadFinished(%s, "%s", "%s");</script>' % \
           (code, message, thumb_name)
