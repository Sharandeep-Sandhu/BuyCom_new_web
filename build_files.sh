#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files (important for admin panel & frontend)
python manage.py collectstatic --noinput --clear

# Optional: Run migrations (if you have database)
# python manage.py migrate --noinput