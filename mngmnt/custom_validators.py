# -*- coding: utf-8 -*-
import re
from django.core.exceptions import ValidationError

__author__ = 'PervinenkoVN'

def login_validator(value):
    if not re.match('^[a-z0-9]+$', value):
        raise ValidationError(u'Логин должен состоять из латинских букв и/или цифр')
