from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models.user import User
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from restaurantCommande.models.commande import Commande


class NoteRestaurantDrink(models.Model):
    """Docstring for class."""

    drink = models.ForeignKey(RestaurantDrink, on_delete=models.CASCADE)
    note = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=None)
    comment = models.TextField(null=True, blank=True, default=None)


class NoteRestaurantFood(models.Model):
    """Docstring for class."""

    food = models.ForeignKey(RestaurantFood, on_delete=models.CASCADE)
    note = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=None)
    comment = models.TextField(null=True, blank=True, default=None)


class NoteRestaurant(models.Model):
    """Docstring for class."""

    note = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=None)
    comment = models.TextField(null=True, blank=True, default=None)
    foods = models.ManyToManyField(NoteRestaurantFood)
    drinks = models.ManyToManyField(NoteRestaurantDrink)


class NoteDelivery(models.Model):
    """Docstring for class."""

    note = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=None)
    comment = models.TextField(null=True, blank=True, default=None)


class NoteService(models.Model):
    """Docstring for class."""

    reference = models.CharField(max_length=100)
    note_delivery = models.ForeignKey(NoteDelivery, default=None, null=True, on_delete=models.CASCADE)
    note_restaurant = models.ForeignKey(NoteRestaurant, default=None, null=True, on_delete=models.CASCADE)
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE
    )
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
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.reference


@receiver(post_save, sender=NoteService, dispatch_uid="update_note_service_reference")
def update_note_service_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'NOT_SER_' + str(instance.id).zfill(8)
        instance.save()
