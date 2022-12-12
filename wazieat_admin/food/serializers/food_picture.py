from rest_framework import serializers
from food.models.food_picture import FoodImage, FoodPicture
from drf_writable_nested import WritableNestedModelSerializer


class FoodImageSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    image = serializers.ImageField(allow_null=False, allow_empty_file=False)

    class Meta:
        """Docstring for class."""

        model = FoodImage
        fields = ['id', 'image']


class FoodPictureSerializer(WritableNestedModelSerializer):
    """Docstring for class."""

    images = FoodImageSerializer(many=True)

    def update(self, instance, validated_data):
        if instance.images.all():
            instance.images.through.objects.all().delete()
        instance.name = validated_data['name']
        instance.description = validated_data['description']
        for f in validated_data['images']:
            val = FoodImage()
            val.image = f['image']
            val.save()
            instance.images.add(val)
        instance.save()
        return instance

    class Meta:
        """Docstring for class."""

        model = FoodPicture
        fields = ['id', 'name', 'description', 'images', 'reference',
                  'created_by', 'created_at', 'updated_at']
        read_only_fields = ['reference', 'created_by', 'created_at', 'updated_at']
