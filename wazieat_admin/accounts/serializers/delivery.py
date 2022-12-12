from accounts.models.delivery import Delivery
from rest_framework import serializers
from accounts.models.user import User
from drf_writable_nested import WritableNestedModelSerializer
import datetime


def current_year():
    return datetime.date.today().year


class DeliveryClassSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    brand = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    model = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    power = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    year_motor = serializers.IntegerField(required=False, max_value=datetime.date.today().year, min_value=1969)
    has_motor = serializers.BooleanField(required=True)
    scan_cni = serializers.ImageField(required=True)
    has_permis = serializers.BooleanField(required=True)
    location = serializers.ListField(required=False, child=serializers.FloatField())
    address = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    date_of_birth = serializers.DateField(required=True)

    class Meta:
        """Docstring for class."""

        model = Delivery
        fields = ['id', 'date_of_birth', 'scan_cni', 'address', 'has_permis',
                  'has_motor', 'brand', 'model', 'power', 'year_motor', 'location']
        read_only = []


class DeliverySerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    delivery = DeliveryClassSerializer(required=True)
    picture = serializers.ImageField(required=True, allow_null=True)
    email = serializers.EmailField(required=True, allow_null=True, allow_blank=False)

    class Meta:
        """Docstring for class."""

        model = User
        fields = ['id', 'phone', 'email', 'picture', 'last_name', 'first_name',
                  'is_active', 'reference', 'pseudo', 'delivery']
        read_only_fields = ['is_active', 'reference']


class DeliveryCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    phone = serializers.RegexField(required=True, regex=r'^\+?1?\d{9,15}$')
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=True)
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    pseudo = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    picture = serializers.ImageField(required=True, allow_null=True)
    delivery = DeliveryClassSerializer(required=True)
