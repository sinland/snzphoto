# -*- coding: utf-8 -*-
import json
import string
import re
from django.http import HttpResponse

__author__ = 'PervinenkoVN'

def translit(msg):
    msg = string.lower(msg)
    if isinstance(msg, unicode):
        dict = {
            u'а' : 'a',
            u'б' : 'b',
            u'в' : 'v',
            u'г' : 'g',
            u'д' : 'd',
            u'е' : 'e',
            u'ё' : 'ye',
            u'ж' : 'jh',
            u'з' : 'z',
            u'и' : 'i',
            u'й' : 'y',
            u'к' : 'k',
            u'л' : 'l',
            u'м' : 'm',
            u'н' : 'n',
            u'о' : 'o',
            u'п' : 'p',
            u'р' : 'r',
            u'с' : 's',
            u'т' : 't',
            u'у' : 'u',
            u'ф' : 'f',
            u'х' : 'h',
            u'ц' : 'ts',
            u'ч' : 'ch',
            u'ш' : 'sh',
            u'щ' : 'sch',
            u'ъ' : '',
            u'ы' : 'i',
            u'ь' : '',
            u'э' : 'e',
            u'ю' : 'yu',
            u'я' : 'ya',
            }
    else:
        return msg
    result = ''
    for c in msg:
        if c in dict.keys():
            result += dict[c]
        else:
            result += c
    result = re.sub('\W+', '-', result)
    if result.endswith('-'):
        result = result[:len(result) - 1]
    return result


def get_json_response(code, values = {} , message = ''):
    values['code'] = code
    values['message'] = message
    return HttpResponse(json.dumps(values))

"""
parsing link to shared video to find 'iframe' or 'object' tags. returns reconstructured tags
"""
def clean_embedded_video_link(link):
    clean_tag = ""
    iframe = re.search(r'<iframe(?P<args>[^>]+)>(?:.*)</iframe>', link, flags=re.I)
    obj = re.match(r'<object(?P<attrs>[^>]+)>(?P<args>.*)</object>', link, flags=re.I)
    if iframe:
        clean_tag = "<iframe %s></iframe>" % iframe.group('args').strip()
        #src = re.search('src=[\'|"]+(.+)[\'|"]+', args)
    elif obj:
        clean_tag = "<object %s>" % obj.group('attrs').strip()
        obj_args = obj.group('args')
        params = re.findall('<param(?P<attrs>[^>]+)>(?:.*)</param>', obj_args)
        for param in params:
            clean_tag += "<param %s></param>" % param.strip()
        embed = re.search('<embed(?:\s*)(?P<attrs>[^>]+)>(?:.*)</embed>', obj_args)
        if embed:
            clean_tag += "<embed %s></embed>" % embed.group('attrs')
        clean_tag += "</object>"
    return clean_tag