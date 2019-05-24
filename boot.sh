#!/bin/sh
source venv/bin/activate
flask db upgrade
flask translate compile
exec gunicorn -b :8000 --access-logfile - --error-logfile - flasky:app
