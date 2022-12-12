from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models.user import User
import datetime
import hashlib


class FoodImage(models.Model):
    """Docstring for class."""

    def foods_directory_path(self, filename):
        """Docstring for function."""
        plain = str(self.image)
        return 'Foods/{0}/{1}'.format(
            hashlib.sha1(
                plain.encode('utf-8')
            ).hexdigest(),
            filename)

    image = models.ImageField(upload_to=foods_directory_path)


class FoodPicture(models.Model):
    """Docstring for class."""

    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    images = models.ManyToManyField(FoodImage)
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


@receiver(post_save, sender=FoodPicture, dispatch_uid="update_food_picture")
def update_food_picture(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'FPIC_' + str(instance.id).zfill(8)
        instance.save()
