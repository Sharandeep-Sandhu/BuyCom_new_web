#!/bin/bash

echo "BUILD START"

# Install dependencies
pip install -r requirements.txt

# Collect static files (very important for your admin panel CSS/JS)
python manage.py collectstatic --noinput --clear

echo "BUILD END"