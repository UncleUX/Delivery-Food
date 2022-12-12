from django.db import models
import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from restaurantMenu.models.menu import Menu
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from django.contrib.postgres.fields import ArrayField
from accounts.models.user import User


class MenuQuantity(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class FoodQuantity(models.Model):
    food = models.ForeignKey(RestaurantFood, on_delete=models.CASCADE)
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class DrinkQuantity(models.Model):
    drink = models.ForeignKey(RestaurantDrink, on_delete=models.CASCADE)
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Commande(models.Model):
    """Docstring for class."""

    STATUS_CHOICES = (
        (1, "Enregistrée"),
        (2, "Validée par le livreur"),
        (3, "En cours de préparation"),
        (4, "En cours de livraison"),
        (5, "Livrée"),
        (6, "Annulée"),
    )

    reference = models.CharField(max_length=100)
    menu = models.ManyToManyField(
        Menu, through=MenuQuantity
    )
    food = models.ManyToManyField(
        RestaurantFood, through=FoodQuantity
    )
    drink = models.ManyToManyField(
        RestaurantDrink, through=DrinkQuantity
    )
    total_price = models.DecimalField(
        max_digits=20, decimal_places=2,
        null=True, blank=True, default=None
    )
    is_restaurant_valid = models.BooleanField(null=True)
    is_delivery_valid = models.BooleanField(null=True)
    is_delivery_check = models.BooleanField(null=True)
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
    restaurant_validate_date = models.DateTimeField(null=True, default=None)
    delivery_validate_date = models.DateTimeField(null=True, default=None)
    restaurant_cancel_date = models.DateTimeField(null=True, default=None)
    delivery_cancel_date = models.DateTimeField(null=True, default=None)
    delivery_check_date = models.DateTimeField(null=True, default=None)
    delivery_date = models.DateTimeField(null=True, default=None)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_user'
    )
    restaurant_validated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name='restaurant_validated_by'
    )
    delivery_validated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name='delivery_validated_by'
    )
    restaurant_cancel_validated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name='restaurant_cancel_validation_user'
    )
    delivery_cancel_validated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name='delivery_cancel_validated_by'
    )
    delivery_location = ArrayField(
        models.FloatField(default=0),
        size=2, null=True, default=None
    )
    token = models.CharField(max_length=10, null=True, blank=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1
    )
    cooking_time = models.TimeField(null=True, blank=True, default=None)
    site_delivery = models.CharField(max_length=255, null=True, blank=True)
    suggestion = models.JSONField(null=True, default=None)
    restaurant_suggest_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name='restaurant_suggest_by'
    )

    def __str__(self):
        return self.reference


@receiver(post_save, sender=Commande, dispatch_uid="update_commande_reference")
def update_commande_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'COM_' + str(instance.id).zfill(8)
        instance.save()



