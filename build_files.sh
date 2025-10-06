#!/usr/bin/env bash
# Exit on error
set -o errexit

# pip komutunu python ile çalışacak şekilde güncelledik
python -m pip install -r requirements.txt

# Statik dosyaları topla
python manage.py collectstatic --no-input