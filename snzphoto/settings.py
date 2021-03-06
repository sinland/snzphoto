import os

# Django settings for snzphoto project.

DIR = os.path.dirname(__file__)
PRODUCTION = True
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('sinland', 'sinland@mail.ru'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DIR, 'snzphotosite.s3db'),
    }
}

if PRODUCTION:
    STATIC_ROOT = os.path.join(os.path.expanduser('~'), 'domains/snzfoto.sinland.myjino.ru/static/')
    MEDIA_URL = 'http://snzfoto.sinland.myjino.ru/media/'
    MEDIA_ROOT = os.path.join(os.path.expanduser('~'), 'domains/snzfoto.sinland.myjino.ru/media/')
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.join(os.path.expanduser('~'), 'django/snzfoto/cache_files'),
        }
    }
    STATICFILES_DIRS = ()
else:
    STATIC_ROOT = 'd:/Development/python/snzphoto_static_files/'
    MEDIA_URL = 'http://media.sinland.ru/'
    MEDIA_ROOT = 'd:/WebServers/home/sinland.ru/media/'
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': 'd:/Development/python/snzphoto/cache_files',
            }
    }
    STATICFILES_DIRS = (
        'd:/Development/python/snzphoto/static_files/',
    )

IMG_THUMBS_SIZE = (350, 350)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Yekaterinburg'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'j@kq(7i#tzcr)jm$(4*kyb5_0*!yb3y8d2an*vm5s8)22=!qgw'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'snzphoto.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'snzphoto.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DIR, '..\\templates').replace('\\', '/'),
)
TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.core.context_processors.request",
                               "django.contrib.messages.context_processors.messages",
                               "snzphoto.context_processors.settings_appender")

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'snzphoto',
    'news',
    'photos',
    'videos',
    'mngmnt',
    'debates'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] [%(asctime)s]: (%(module)s) %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    'file_dump' : {
        'level' : 'DEBUG',
        'class' : 'logging.FileHandler',
        'filename' : os.path.join(DIR, 'snzphotosite.log'),
        'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'manager-news' : {
            'handlers' : ['file_dump'],
            'level' : 'ERROR',
            'propagate' : True
        },
        'manager-videos' : {
            'handlers' : ['file_dump'],
            'level' : 'INFO',
            'propagate' : True
        },
        'admin.photo_views' : {
            'handlers' : ['file_dump'],
            'level' : 'ERROR',
            'propagate' : True
        }
    }
}

NEWS_PER_PAGE = 3
RECAPCHA_API_KEY = "6LeGA-YSAAAAAPAFRsVnstFn04RCiuSwjE1cxaA5"
RECAPCHA_PRIVATE_API_KEY = "6LeGA-YSAAAAAI-7ZUzJYg09R37jYAI5Hc5_waYA"

