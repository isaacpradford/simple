#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Command to run the server: python3 manage.py runserver
# Command to run the server with gunicorn: python3 -m gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker
# Command to run it from root: PYTHONPATH=backend python3 -m gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker
# Command to make db migration: python3 manage.py makemigrations
# Command to run db migration: python3 manage.py migrate

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
