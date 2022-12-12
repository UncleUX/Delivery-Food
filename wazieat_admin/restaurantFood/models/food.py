from django.db import models
import datetime
import hashlib
from django.dispatch import receiver
from django.db.models.signals import post_save
from food.models.type import FoodType
from food.models.category import FoodCategory
from food.models.food_picture import FoodImage
from restaurantFood.models.ingredient import Ingredient
from accounts.models.user import User


class RestaurantFood(models.Model):
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
    foodType = models.ForeignKey(
        FoodType,
        on_delete=models.PROTECT
    )
    foodCategory = models.ForeignKey(
        FoodCategory,
        on_delete=models.PROTECT
    )
    foodPicture = models.ImageField(
        upload_to=restaurant_directory_path, null=True, default=None)
    foodPicture_related = models.ForeignKey(
        FoodImage, null=True, default=None, on_delete=models.CASCADE)
    nutritional_value = models.TextField(null=True, default=None)
    price = models.FloatField(default=0)
    ingredients = models.ManyToManyField(
        Ingredient,
        default=None
    )
    activated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activate_food',
        null=True, default=None)
    activated_reason = models.TextField(null=True, default=None)
    cooking_time = models.TimeField(null=True, default=None)
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
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.name


@receiver(post_save, sender=RestaurantFood, dispatch_uid="update_restaurantfood_reference")
def update_restaurantfood_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'RES_FO_' + str(instance.id).zfill(8)
        instance.save()
