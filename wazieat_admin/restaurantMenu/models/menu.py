from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from django.core.validators import MaxValueValidator, MinValueValidator
from .publicationPeriod import PublicationPeriod
from accounts.models.user import User


class Menu(models.Model):
    """Docstring for class."""

    STATUS_PRICE = (
        (1, 'Percent'),
        (2, 'Real'),
    )

    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    foods = models.ManyToManyField(
        RestaurantFood
    )
    drinks = models.ManyToManyField(
        RestaurantDrink
    )
    calculated_price = models.FloatField(
        null=True, blank=True, default=None
    )
    real_price = models.FloatField(
        null=True, blank=True, default=None)
    status_price = models.IntegerField(choices=STATUS_PRICE)
    percent = models.FloatField(
        validators=[MinValueValidator(-100.0), MaxValueValidator(100.0)],
        default=None,
        null=True,
        blank=True
    )
    period = models.ForeignKey(
        PublicationPeriod,
        on_delete=models.PROTECT,
        null=True
    )
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
        return self.name


@receiver(post_save, sender=Menu, dispatch_uid="update_menu_reference")
def update_menu_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'MEN_' + str(instance.id).zfill(8)
        instance.save()
