FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache gcc musl-dev

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

COPY wait_for_db.sh /wait_for_db.sh
RUN chmod +x /wait_for_db.sh

CMD sh -c "/wait_for_db.sh && python manage.py migrate && python manage.py collectstatic --noinput && exec gunicorn secret_notes_project.wsgi:application --bind 0.0.0.0:8008"
