from .base import *
import environ

env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEV_DEBUG', default=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DEV_SECRET_KEY', default='django-insecure-default-key-for-development')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from .local import *
except ImportError:
    pass
