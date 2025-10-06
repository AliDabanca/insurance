#!/usr/bin/env bash
# Exit on error
set -o errexit

# pip komutunu python3 ile çalışacak şekilde güncelledik
python3 -m pip install -r requirements.txt

# Statik dosyaları topla
python3 manage.py collectstatic --no-input