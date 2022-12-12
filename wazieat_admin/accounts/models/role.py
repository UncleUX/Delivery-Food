from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Permission
from .restaurant import Restaurant


class RoleManager(models.Manager):
    """Docstring for class."""

    use_in_migrations = True

    def get_by_natural_key(self, name):
        """Docstring for class."""
        return self.get(name=name)


class Role(models.Model):
    """Docstring for class."""

    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
    )

    objects = RoleManager()

    class Meta:
        """Docstring for class."""

        verbose_name = 'role'
        verbose_name_plural = 'roles'

    def __str__(self):
        """Docstring for function."""
        return self.name

    def natural_key(self):
        """Docstring for function."""
        return self.name

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.PROTECT,
        null=True,
        blank=True
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


@receiver(post_save, sender=Role, dispatch_uid="update_role_reference")
def update_role_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'ROL_' + str(instance.id).zfill(8)
        instance.save()
