from django.db import models
from accounts.models.user import User
from restaurantMenu.models.menu import Menu
from django.dispatch import receiver
from django.db.models.signals import post_save


class Comments(models.Model):
    """Docstring for class."""

    reference = models.CharField(max_length=100)
    comment = models.TextField()
    client = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(
        db_column="created_date",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        db_column="updated_date",
        auto_now_add=True
    )


@receiver(post_save, sender=Comments, dispatch_uid="update_comments_reference")
def update_comments_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'COM_' + str(instance.id).zfill(8)
        instance.save()
