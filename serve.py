"""
Production server entry point for Windows.
Uses Waitress WSGI server — run via Task Scheduler on startup.
"""

import os
import sys
import logging

# Ensure working directory is always the app root,
# regardless of how this script is launched (e.g. Task Scheduler)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from waitress import serve
from wsgi import app

# Basic logging to file so you can diagnose issues without a console
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'waitress.log'),
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    logging.info('IT Support — Waitress server starting on port 5008')
    serve(
        app,
        host='0.0.0.0',
        port=5008,
        threads=6,
        channel_timeout=120,
        cleanup_interval=30,
    )
