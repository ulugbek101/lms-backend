import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PROJECT.settings")
app = Celery("PROJECT")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "update-group-status-every-day": {
        "task": "app_auth.tasks.update_group_status",
        "schedule": crontab(hour=0, minute=0),
    }
}
