# File sets up the django environment, used by other scripts that need to
# execute in django land
import os
import django
from django.conf import settings

ORSAY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'orsay'))

TEMPLATE_DIRS = [
    os.path.abspath(os.path.join(ORSAY_DIR, 'templates')),
]

def boot_django(extra_template_dirs=[]):
    for d in extra_template_dirs:
        TEMPLATE_DIRS.append(d)

    settings.configure(
        BASE_DIR=ORSAY_DIR,
        DEBUG=True,
        DATABASES={
            'default':{
                'ENGINE':'django.db.backends.sqlite3',
                'NAME': os.path.join(ORSAY_DIR, 'db.sqlite3'),
            }
        },
        ROOT_URLCONF='orsay.tests.urls',
        MIDDLEWARE = (
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'orsay',
        ),
        TEMPLATES = [{
            'BACKEND':'django.template.backends.django.DjangoTemplates',
            'DIRS':TEMPLATE_DIRS,
            'APP_DIRS':True,
            'OPTIONS': {
                'context_processors':[
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ]
            }
        }],
    )
    django.setup()
