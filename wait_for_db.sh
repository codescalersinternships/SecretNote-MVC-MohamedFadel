#!/bin/sh
until python manage.py dbshell -c "SELECT 1;" > /dev/null 2>&1; do
    echo "Waiting for database to be ready..."
    sleep 1
done
