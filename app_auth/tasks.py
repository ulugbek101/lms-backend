from celery import shared_task
from django.utils import timezone
from .models import Group


@shared_task
def updated_group_status():
    """Updates is_active field of all groups based on the current date"""
    today = timezone.localdate()
    groups = Group.objects.all()
    updated_groups = []

    for group in groups:
        if group.start_date == today and today < group.end_date:
            group.is_active = True
        elif group.start_date > today:
            group.is_active = False
        elif group.start_date < today and today == group.end_date:
            group.is_active = False
        else:
            group.is_active = True
        updated_groups.append(group)

    Group.objects.bulk_update(updated_groups, ["is_active"])
