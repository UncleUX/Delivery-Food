import datetime
import hashlib
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models.module import Module
from drink.models.type import DrinkType
from drink.models.category import DrinkCategory
from food.models.category import FoodCategory
from food.models.type import FoodType
from django_tenants.models import DomainMixin, TenantMixin
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField


class Domain(DomainMixin):
    """Docstring for class."""
    pass


class Picture(models.Model):

    def restaurant_picture_path(self, filename):
        """Docstring for function."""
        time = datetime.datetime.now().isoformat()
        return 'Restaurants/Pictures/{0}'.format(
            filename)

    image = models.ImageField(upload_to=restaurant_picture_path)


class Restaurant(TenantMixin, models.Model):
    """Docstring for class."""

    def restaurant_directory_path(self, filename):
        """Docstring for function."""
        time = datetime.datetime.now().isoformat()
        plain = self.name + '\0' + time
        return '{0}/{1}/{2}'.format(
            hashlib.sha1(
                self.schema_name.encode('utf-8')
            ).hexdigest(),
            hashlib.sha1(
                plain.encode('utf-8')
            ).hexdigest(),
            filename)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

    reference = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, null=True, default=None)
    immatriculation = models.CharField(max_length=255, null=True, default=None)
    social_network_link = ArrayField(models.URLField(max_length=200), size=2, null=True, default=None)
    internet_site = models.URLField(max_length=255, null=True, default=None)
    restaurant_channel = models.IntegerField(null=True, default=None)
    opening_hour = models.TimeField(null=True, default=None)
    closing_hour = models.TimeField(null=True, default=None)
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True, null=True, default=None)
    rccm_document = models.FileField(upload_to=restaurant_directory_path)
    profile_picture = models.ImageField(upload_to=restaurant_directory_path, null=True, default=None)
    picture_restaurant = models.ManyToManyField(Picture)
    is_active = models.BooleanField(default=False)
    activate_date = models.DateTimeField(null=True, default=None)
    activate_reason = models.TextField(default=None, null=True)
    activate_by = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name='activate_by'
    )
    location = ArrayField(
        models.FloatField(default=0),
        size=2, null=True, default=None
    )
    created_at = models.DateTimeField(
            db_column="created_date",
            auto_now_add=True
    )
    updated_at = models.DateTimeField(
            db_column="updated_date",
            auto_now=True
    )
    module = models.ManyToManyField(
        Module,
        default=None
    )
    drinkType = models.ManyToManyField(
        DrinkType,
        blank=True,
        default=None
    )
    drinkCategory = models.ManyToManyField(
        DrinkCategory,
        blank=True,
        default=None
    )
    foodCategory = models.ManyToManyField(
        FoodCategory,
        blank=True,
        default=None
    )
    foodType = models.ManyToManyField(
        FoodType,
        blank=True,
        default=None
    )
    # schema will be automatically created and synced when it is saved
    auto_create_schema = True

    # schema will be automatically drop
    auto_drop_schema = True

    def __str__(self):
        return self.name


@receiver(post_save, sender=Restaurant, dispatch_uid="update_restaurant_reference")
def update_restaurant_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'RES_' + str(instance.id).zfill(8)
        instance.save()
