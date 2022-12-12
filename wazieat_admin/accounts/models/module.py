from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Module(models.Model):
    """Docstring for class."""

    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contenttypes = models.ManyToManyField(
        ContentType
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        db_column="creation_date",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        db_column="modification_date",
        auto_now=True
    )

    def __str__(self):
        """Docstring for function."""
        return self.reference + self.name


@receiver(post_save, sender=Module, dispatch_uid="update_module_reference")
def update_module_reference(instance, **kwargs):
    """Docstring for function."""
    if not instance.reference:
        instance.reference = 'MOD_' + str(instance.id).zfill(8)
        instance.save()
