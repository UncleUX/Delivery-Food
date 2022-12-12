from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models.user import User
from restaurantFood.models.food import RestaurantFood
from restaurantDrink.models.drink import RestaurantDrink
from restaurantCommande.models.commande import Commande


class NoteDrink(models.Model):
    """Docstring for class."""

    drink = models.ForeignKey(RestaurantDrink, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True, default=None)


class NoteFood(models.Model):
    """Docstring for class."""

    food = models.ForeignKey(RestaurantFood, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True, default=None)


class NoteComments(models.Model):
    """Docstring for class."""

    comment = models.TextField(null=True, blank=True, default=None)
    foods = models.ManyToManyField(NoteFood)
    drinks = models.ManyToManyField(NoteDrink)


class Note(models.Model):
    """Docstring for class."""

    reference = models.CharField(max_length=100)
    comments = models.ForeignKey(NoteComments, default=None, null=True, on_delete=models.CASCADE)
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


@receiver(post_save, sender=Note, dispatch_uid="update_note_reference")
def update_note_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'NOT_' + str(instance.id).zfill(8)
        instance.save()
