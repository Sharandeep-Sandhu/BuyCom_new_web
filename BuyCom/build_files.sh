#!/bin/bash

echo "🚀 BUILD START"

# Install dependencies from root requirements.txt
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

echo "✅ BUILD END"