from snzphoto import settings

__author__ = 'PervinenkoVN'

def settings_appender(r):
    return  {
        'media_url_base' : settings.MEDIA_URL,
        'is_debug' : settings.DEBUG,
        'recapcha_api_key' : settings.RECAPCHA_API_KEY
    }