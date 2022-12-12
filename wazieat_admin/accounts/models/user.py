from django.db import models
import hashlib
import random
from django.dispatch import receiver
from django.db.models.signals import post_save
import datetime
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .restaurant import Restaurant
from .delivery import Delivery
from django.core.validators import RegexValidator
from .role import Role


class UserManager(BaseUserManager):
    """Docstring for class."""

    def update_user(self, password, user):
        """Docstring for function create_user."""

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, phone, email, restaurant, last_name,
                    first_name):
        """Docstring for function create_user.

        Returns:
            object: 
        """
        if not email:
            raise ValueError('User must have an email address')

        new_user = self.model(
            phone=phone,
            email=self.normalize_email(email),
            last_name=last_name,
            first_name=first_name,
            restaurant=restaurant
        )

        new_user.save(using=self._db)

        return new_user

    def create_superuser(self, phone, email, last_name, first_name,
                         restaurant=None):
        """Docstring for function."""
        new_user = self.create_user(
            phone=phone,
            email=email,
            restaurant=restaurant,
            last_name=last_name,
            first_name=first_name
        )
        new_user.is_admin = True
        new_user.is_staff = True
        new_user.save(using=self._db)

        return new_user

    def create_admin(self, phone, email, restaurant, last_name,
                     first_name):
        """Docstring for function."""
        new_user = self.create_user(
            phone=phone,
            email=email,
            restaurant=restaurant,
            last_name=last_name,
            first_name=first_name
        )
        new_user.is_admin = False
        new_user.is_staff = True
        new_user.is_active = False
        new_user.save(using=self._db)

        return new_user

    def make_random_password(self, length=10,
                             allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                           'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                           '23456789'):

        characters = list('abcdefghijklmnopqrstuvwxyz')

        characters.extend(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))

        characters.extend(list('0123456789'))

        characters.extend(list('!@#$%^&*()?><:;'))

        password = ''
        for x in range(length):
            password += random.choice(characters)
        return password


class User(AbstractBaseUser, models.Model):
    """Docstring for class."""

    def user_directory_path(self, filename):
        """Docstring for function."""
        time = datetime.datetime.now().isoformat()
        plain = str(self.phone) + '\0' + time
        return 'User/{0}/{1}'.format(
            hashlib.sha1(
                plain.encode('utf-8')
            ).hexdigest(),
            filename)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

    reference = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=100, null=True, blank=False)
    picture = models.ImageField(upload_to=user_directory_path, default=None, null=True)
    pseudo = models.CharField(max_length=100, unique=True, null=True, blank=True, default=None)
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True, null=True, default=None)
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        db_column="creation_date",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        db_column="modification_date",
        auto_now=True
    )
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_requested_at = models.DateTimeField(null=True, blank=True)
    roles = models.ManyToManyField(Role, related_name="roles", blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['restaurant']

    auto_create_schema = True

    def __str__(self):
        """Docstring for function."""
        return self.email

    def is_super(self):
        """Docstring for function."""
        return self.is_admin and self.is_staff

    def has_perm(self, perm):
        """Docstring for function."""
        parts = perm.split('.')
        has = False
        if self.is_staff:
            if self.restaurant is not None:
                if self.restaurant.module:
                    for mod in self.restaurant.module.all():
                        for contenttype in mod.contenttypes.all():
                            perms = Permission.objects.all().filter(
                                content_type=contenttype)
                            for permission in perms:
                                if permission.codename == parts[1]:
                                    has = True
            elif self.is_admin:
                perms = Permission.objects.all()
                for permission in perms:
                    if permission.codename == parts[1]:
                        has = True
            else:
                for role in self.roles.all():
                    for permission in role.permissions.all():
                        if permission.codename == parts[1]:
                            has = True
        else:
            for role in self.roles.all():
                for permission in role.permissions.all():
                    if permission.codename == parts[1]:
                        has = True
        return has

    def requested_token_valid(self):
        """Docstring for function."""
        time = timezone.now()
        second = self.password_requested_at + datetime.timedelta(hours=24)
        if time > second:
            return False
        return True

    def get_permissions(self):
        """Docstring for function."""
        permissions = []
        if self.restaurant is not None:
            if self.restaurant.module:
                if self.is_staff:
                    for mod in self.restaurant.module.all():
                        for contenttype in mod.contenttypes.all():
                            perms = Permission.objects.all().filter(
                                content_type=contenttype)
                            for perm in perms:
                                if perm.codename not in permissions:
                                    permissions.append(perm.codename)
                else:
                    for role in self.roles.all():
                        # roles.append(role.name)
                        for permission in role.permissions.all():
                            permissions.append(permission.codename)
            else:
                if self.is_staff:
                    perms = Permission.objects.all()
                    for permission in perms:
                        permissions.append(permission.codename)
                else:
                    for role in self.roles.all():
                        # roles.append(role.name)
                        for permission in role.permissions.all():
                            permissions.append(permission.codename)
        else:
            if self.is_staff:
                perms = Permission.objects.all()
                for permission in perms:
                    permissions.append(permission.codename)
            else:
                for role in self.roles.all():
                    # roles.append(role.name)
                    for permission in role.permissions.all():
                        permissions.append(permission.codename)

        return permissions


@receiver(post_save, sender=User, dispatch_uid="update_user_reference")
def update_user_reference(instance, **kwargs):
    if not instance.reference:
        instance.reference = 'USR_' + str(instance.id).zfill(8)
        instance.save()
