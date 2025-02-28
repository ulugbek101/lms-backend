# Learning Management System (Backend)
Learning management system for private schools and learning centers


- Clone repository
```bash
git clone https://github.com/ulugbek101/lms-backend.git
```

- Create virtual environment
```bash
# MacOS / Linux
python3 -m venv .venv

# Windows
python -m venv .venv
```

- Install dependencies
```bash
pip install -r requiremnts.txt
```

- Create .env file to store secret credentials
```
# Django
DJANGO_SECRET_KEY=<YOUR_DJANGO_SECRET_KEY>
DEBUG=1  # 1 or 0 meaning True or False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Not required if you are working in development (DEBUG=True) mode, if you turn DEBUG=False, then fill out thee fields, settings.py switches postgres database automatically
DB_NAME=
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=

# Eskiz (SMS provider)
ESKIZ_EMAIL=
ESKIZ_SECRET_TOKEN=
```

- Make the migrations if you add or change some model before running, if you don't, just skip this step
```bash
python manage.py makemigrations
```

- Mmigrate models into a new database
```bash
python manage.py migrate
```


- Run a server and navigate to https://127.0.0.1:8000/api/v1/ to see all available endpoints
```bash
python manage.py runserver
```




