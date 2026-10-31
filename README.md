# Quartico (quartico.co) — Django online shop

## Run locally
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py makemigrations shop
    python manage.py migrate
    python manage.py seed              # demo products
    python manage.py createsuperuser   # admin at /admin/
    python manage.py runserver

## Production
Set DJANGO_DEBUG=0, DJANGO_SECRET_KEY=<long random>, DJANGO_ALLOWED_HOSTS=quartico.co and serve over HTTPS
(gunicorn + nginx); run `python manage.py collectstatic`. Replace sqlite with PostgreSQL for real use.
