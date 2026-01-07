#!/bin/bash

# Exit on error
set -e

# Change to the application directory
cd /var/app/current

source /var/app/venv/*/bin/activate
pip install --no-input -r requirements.txt
python manage.py migrate --noinput
