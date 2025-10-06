#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

# Statik dosyaları topla
python manage.py collectstatic --no-input