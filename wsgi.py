"""
Production WSGI entry point for Gunicorn or Waitress.

Gunicorn:
    gunicorn --config gunicorn.conf.py wsgi:app

Waitress (Windows):
    waitress-serve --host=0.0.0.0 --port=8000 wsgi:app
"""
import os
from app import create_app

app = create_app('production')
