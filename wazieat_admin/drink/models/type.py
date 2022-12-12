from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save


class DrinkType(models.Model):
    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        db_column="created_date",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        db_column="updated_date",
        auto_now_add=True
    )

    def __str__(self):
        return self.name


@receiver(post_save, sender=DrinkType, dispatch_uid="update_drinktype_reference")
def update_drinktype_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'DR_TYP_' + str(instance.id).zfill(8)
        instance.save()
