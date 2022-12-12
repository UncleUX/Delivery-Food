from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models.user import User
from drink.models.category import DrinkCategory
import datetime
import hashlib


class Drink(models.Model):
    """Docstring for class."""

    def drinks_directory_path(self, filename):
        """Docstring for function."""
        plain = str(self.name)
        return 'Drinks/{0}/{1}'.format(
            hashlib.sha1(
                plain.encode('utf-8')
            ).hexdigest(),
            filename)

    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    drinkCategory = models.ForeignKey(
        DrinkCategory,
        on_delete=models.PROTECT,
        related_name='drink'
    )
    drinkPicture = models.ImageField(upload_to=drinks_directory_path, null=True, default=None)
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

    def __str__(self):
        return self.reference


@receiver(post_save, sender=Drink, dispatch_uid="update_drink")
def update_drink(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'DRINK_' + str(instance.id).zfill(8)
        instance.save()
