#!/usr/bin/env bash
# Exit on error
set -o errexit

# pip komutunu python3 ile çalışacak şekilde güncelledik
python3 -m pip install -r requirements.txt

# Statik dosyaları topla (Output'u daha görünür yapmak için 'input yok' bayrağını kullanmaya devam ediyoruz)
echo "Collecting static files to STATIC_ROOT..."
python3 manage.py collectstatic --no-input

# Vercel'in çıktıyı doğru algıladığından emin olmak için toplanan dosyaları listele
echo "Listing collected static files in STATIC_ROOT (./staticfiles):"
ls -R ./staticfiles
