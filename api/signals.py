from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Expense, Payment


@receiver(signal=post_save, sender=Payment)
def save_payment_extra_details(sender, instance, created, **kwargs):
    """
    Save payment's extra details if student, or a group attached to a payment is deleted
    """
    if created:
        instance.student_name = instance.student.full_name
        instance.group_name = instance.group.name
        instance.save()


@receiver(signal=post_save, sender=Expense)
def save_expense_extra_details(sender, instance, created, **kwargs):
    """
    Set expense's extra details to keep details if user assigned expense or a user, for whom this expense was
    created is deleted
    """
    if created:
        instance.assigned_by_name = instance.assigned_by.full_name
        instance.assigned_to_name = instance.assigned_to.full_name
        instance.save()
