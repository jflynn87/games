"""
Django settings for gamesProj project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
MODULE_DIR = os.path.dirname(__file__)  # get current directory
file_path = os.path.join(MODULE_DIR, 'name_fix.txt')





# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!

if os.environ.get("DEBUG") == "True":
   DEBUG = True
else:
   DEBUG = False


ALLOWED_HOSTS = ['jflynn87.pythonanywhere.com', '127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mathfilters',
    'django_select2',
    'bootstrapform',
    'django.contrib.humanize',
    'rest_framework',
    'corsheaders',
    'fb_app',
    'golf_app',
    'run_app',
    'port_app',
    'user_app',
    ]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    

]

ROOT_URLCONF = 'gamesProj.urls'

CORS_URLS_REGEX = r'^/api.*'
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    
    'http://localhost:3030',
#    'your-bucket-here.s3-us-west-2.amazonaws.com',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': 
        ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    'DEFAULT_RENDERER_CLASSES': 
        ['rest_framework.renderers.JSONRenderer']

    
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR,],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gamesProj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


#before google cloud, used to line 104
#DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
#}

#for google cloud deployment
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# Install PyMySQL as mysqlclient/MySQLdb to use Django's mysqlclient adapter
# See https://docs.djangoproject.com/en/2.1/ref/databases/#mysql-db-api-drivers
# for more information
#import pymysql  # noqa: 402
#pymysql.install_as_MySQLdb()
import MySQLdb
#
# # [START db_setup]
#
db_password = os.environ.get('orig_games_db_password')
if os.environ.get("DEBUG") != "True":
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.mysql',
              'HOST': 'jflynn87.mysql.pythonanywhere-services.com',
              'USER': 'jflynn87',
              'PASSWORD': db_password,
              'NAME': 'jflynn87$orig_games',
              'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
          }
      }
else:
      print ('local')
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.mysql',
#              'HOST': '127.0.0.1',
#              'PORT': '3306',
              'NAME': 'orig_games',
              'USER': 'orig_games',
              'PASSWORD': db_password,
              'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
          }
      }
# [END db_setup]


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'America/New_York'
TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

#STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static-cdn-local')
STATIC_ROOT = os.path.join(STATIC_DIR, 'static-cdn-local')
STATICFILES_DIRS = [
    STATIC_DIR,
        
]
#STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, 'static'), 
#]

#STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static-cdn-local')




EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
user = os.environ.get('GOLF_email_id')
pwd = os.environ.get('GOLF_email_password')


# using debug setting to determine test vs. prod
if DEBUG  == True:
    user_no_quotes = user.strip("'")
    pwd_no_quotes= pwd.strip("'")
    EMAIL_HOST_USER = user_no_quotes
    EMAIL_HOST_PASSWORD = pwd_no_quotes
else:
    EMAIL_HOST_USER = user
    EMAIL_HOST_PASSWORD = pwd

EMAIL_PORT = 587



LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = "/"

INTERNAL_IPS = ['127.0.0.1']
