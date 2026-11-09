#!/bin/sh
set -e
python manage.py migrate --noinput
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell -c "import os; from django.contrib.auth.models import User; u=os.environ.get('DJANGO_SUPERUSER_USERNAME','admin'); User.objects.filter(username=u).exists() or User.objects.create_superuser(u, 'admin@example.test', os.environ['DJANGO_SUPERUSER_PASSWORD'])"
fi
exec "$@"
