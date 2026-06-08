"""
WSGI config for file_locker_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_locker_project.settings')

application = get_wsgi_application()

# Run migrations programmatically when deploying to Vercel
if os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ:
    from django.core.management import call_command
    try:
        print("Running migrations on Vercel startup...")
        call_command('migrate', interactive=False)
        print("Migrations completed successfully.")
    except Exception as e:
        print(f"Error running migrations: {e}")

app = application
