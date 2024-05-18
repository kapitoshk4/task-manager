#!/usr/bin/env bash
# exit on error
set -0 errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate