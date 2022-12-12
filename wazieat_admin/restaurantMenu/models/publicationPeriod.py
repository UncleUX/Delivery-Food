from django.db import models
import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models.user import User


class PublicationPeriod(models.Model):
    """Docstring for class."""

    DAYS_OF_WEEK = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    )

    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    menu_day = models.PositiveIntegerField(choices=DAYS_OF_WEEK)
    end_date = models.DateField(null=True, blank=True)
    repeat = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        db_column="created_date",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        db_column="updated_date",
        auto_now=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True
    )


@receiver(post_save, sender=PublicationPeriod, dispatch_uid="update_period_reference")
def update_period_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'PP_' + str(instance.id).zfill(8)
        instance.save()

