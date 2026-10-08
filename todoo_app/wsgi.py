"""
WSGI config for todoo_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoo_app.settings')

# Automatically run migrations on startup for serverless
try:
    call_command('migrate')
except Exception as e:
    print(f"Migration error: {e}")

application = get_wsgi_application()
app = application