import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get('CARTOGEO_DATA_DIR', BASE_DIR / 'dados')).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
secret_file = DATA_DIR / 'secret.key'
if not secret_file.exists():
    try:
        with secret_file.open('x') as f:
            f.write(secrets.token_urlsafe(64))
    except FileExistsError:
        pass
SECRET_KEY = secret_file.read_text().strip()
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]', 'testserver']
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
                  'django.contrib.messages', 'django.contrib.staticfiles', 'core']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware',
              'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
              'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware',
              'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'cartogeo.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
              'OPTIONS': {'context_processors': ['django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages',
                'core.context.navigation']}}]
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': DATA_DIR / 'cartogeo.sqlite3', 'OPTIONS': {'timeout': 30}}}
AUTH_PASSWORD_VALIDATORS = [
 {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
 {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = DATA_DIR / 'documentos'
LOGIN_URL = '/entrar/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/entrar/'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATA_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
VERSION = '0.5.3'
