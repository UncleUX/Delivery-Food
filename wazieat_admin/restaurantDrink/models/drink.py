from django.db import models
import datetime
import hashlib
from django.dispatch import receiver
from django.db.models.signals import post_save
from drink.models.type import DrinkType
from drink.models.category import DrinkCategory
from drink.models.drink import Drink
from accounts.models.user import User


class RestaurantDrink(models.Model):
    """Docstring for class."""

    def restaurant_directory_path(self, filename):
        """Docstring for function."""
        time = datetime.datetime.now().isoformat()
        plain = self.name + '\0' + time
        return '{0}/{1}/{2}'.format(
            hashlib.sha1(
                self.created_by.restaurant.schema_name.encode('utf-8')
            ).hexdigest(),
            hashlib.sha1(
                plain.encode('utf-8')
            ).hexdigest(),
            filename)

    reference = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    drinkType = models.ForeignKey(
        DrinkType,
        on_delete=models.PROTECT,
        null=True
    )
    drinkCategory = models.ForeignKey(
        DrinkCategory,
        on_delete=models.PROTECT,
        null=True
    )
    price = models.FloatField(default=0)
    admin_drink = models.ForeignKey(
        Drink,
        on_delete=models.PROTECT,
        null=True,
        default=None
    )
    drinkPicture = models.ImageField(
        upload_to=restaurant_directory_path, null=True)
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


@receiver(post_save, sender=RestaurantDrink, dispatch_uid="update_restaurantdrink_reference")
def update_restaurantdrink_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'RES_DR_' + str(instance.id).zfill(8)
        instance.save()
