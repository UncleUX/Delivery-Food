from accounts.models.restaurant import Restaurant, Picture
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from accounts.models.module import Module
from drink.models.type import DrinkType
from drink.models.category import DrinkCategory
from food.models.category import FoodCategory
from food.models.type import FoodType


class PictureSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    class Meta:
        """Docstring for class."""
        model = Picture
        fields = ['id', 'image']


class RestaurantSerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    module = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True
    )
    drinkType = serializers.PrimaryKeyRelatedField(
        queryset=DrinkType.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    drinkCategory = serializers.PrimaryKeyRelatedField(
        queryset=DrinkCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    foodCategory = serializers.PrimaryKeyRelatedField(
        queryset=FoodCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    foodType = serializers.PrimaryKeyRelatedField(
        queryset=FoodType.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    location = serializers.ListField(child=serializers.FloatField())
    picture_restaurant = PictureSerializer(many=True)
    social_network_link = serializers.ListField(child=serializers.URLField())
    email = serializers.CharField(allow_null=True)

    class Meta:
        """Docstring for class."""

        model = Restaurant
        fields = ['id', 'name', 'email', 'phone', 'rccm_document',
                  'profile_picture', 'picture_restaurant', 'created_at', 'updated_at', 'reference',
                  'module', 'drinkType', 'drinkCategory', 'foodCategory', 'foodType',
                  'location', 'social_network_link', 'internet_site', 'restaurant_channel',
                  'opening_hour', 'closing_hour', 'immatriculation']
        read_only_fields = ['reference', 'created_at', 'update_at']


class RestaurantUpdateSerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    module = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True
    )
    drinkType = serializers.PrimaryKeyRelatedField(
        queryset=DrinkType.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    drinkCategory = serializers.PrimaryKeyRelatedField(
        queryset=DrinkCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    foodCategory = serializers.PrimaryKeyRelatedField(
        queryset=FoodCategory.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    foodType = serializers.PrimaryKeyRelatedField(
        queryset=FoodType.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        many=True,
        allow_null=True,
        allow_empty=True
    )
    location = serializers.ListField(child=serializers.FloatField())
    picture_restaurant = PictureSerializer(many=True)
    social_network_link = serializers.ListField(child=serializers.CharField())

    def update(self, instance, validated_data):
        # module
        if instance.module.all():
            instance.module.through.objects.all().delete()
        for f in validated_data['module']:
            instance.module.add(f)
        # drinkCategory
        if instance.drinkCategory.all():
            instance.drinkCategory.through.objects.all().delete()
        for f in validated_data['drinkCategory']:
            instance.drinkCategory.add(f)
        # drinkType
        if instance.drinkType.all():
            instance.drinkType.through.objects.all().delete()
        for f in validated_data['drinkType']:
            instance.drinkType.add(f)
        # foodCategory
        if instance.foodCategory.all():
            instance.foodCategory.through.objects.all().delete()
        for f in validated_data['foodCategory']:
            instance.foodCategory.add(f)
        # foodType
        if instance.foodType.all():
            instance.foodType.through.objects.all().delete()
        for f in validated_data['foodType']:
            instance.foodType.add(f)
        instance.name = validated_data['name']
        instance.phone = validated_data['phone']
        instance.rccm_document = validated_data['rccm_document']
        instance.profile_picture = validated_data['profile_picture']
        instance.social_network_link = validated_data['social_network_link']
        instance.internet_site = validated_data['internet_site']
        instance.location = validated_data['location']
        instance.restaurant_channel = validated_data['restaurant_channel']
        instance.opening_hour = validated_data['opening_hour']
        instance.closing_hour = validated_data['closing_hour']
        instance.immatriculation = validated_data['immatriculation']
        if instance.picture_restaurant.all():
            instance.picture_restaurant.through.objects.all().delete()
        for f in validated_data['picture_restaurant']:
            val = Picture()
            val.image = f['image']
            val.save()
            instance.picture_restaurant.add(val)
        instance.save()
        return instance

    class Meta:
        """Docstring for class."""

        model = Restaurant
        fields = ['id', 'name', 'phone', 'rccm_document',
                  'profile_picture', 'picture_restaurant', 'module', 'drinkCategory',
                  'drinkType', 'foodCategory', 'foodType', 'location',
                  'social_network_link', 'internet_site', 'restaurant_channel',
                  'opening_hour', 'closing_hour', 'immatriculation']

