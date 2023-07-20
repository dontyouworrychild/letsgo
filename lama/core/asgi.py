"""
ASGI config for lama project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from decouple import config

from django.core.asgi import get_asgi_application

environment = config('ENVIRONMENT')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lama.settings.' + environment)

application = get_asgi_application()
