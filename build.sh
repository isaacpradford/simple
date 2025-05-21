#!/usr/bin/env bash

# Exit on error
set -o errexit

pip install -r requirements.txt

# Convert static asset files
python backend/manage.py collectstatic --no-input

# Apply any outstanding database migrations
python backend/manage.py migrate