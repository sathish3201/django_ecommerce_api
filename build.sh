#!/usr/bin/env bash
# exit on error

set -o errexit
pip install -r requirements.txt


python manage.py migrate


python manage.py shell <<EOF 
# check if super already exists
import os
from django.contrib.auth import get_user_model 

# get the envirolment variables
username = os.environ.get("DJANGO_SUPERUSER_USERNAME","admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@gmail.com")
password =os.environ.get("DJANGO_SUPERUSER_PASSWORD","Admin@1234")

User = get_user_model()
#Check if super user exist or not
if not User.objects.filter(username = username).exists():
    User.objects.create_superuser(username= username, email=email, password=password)
EOF

python manage.py collectstatic --no-input