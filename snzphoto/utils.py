# -*- coding: utf-8 -*-

import string
import re

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
            u'й' : 'yi',
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
            u'ц' : 'c',
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