from rest_framework import serializers


class ValidateCommandeSerializer(serializers.Serializer):
    """Docstring for class."""

    valid_status = serializers.BooleanField()
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=255, required=False)


class ValidateCommandeCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    valid_status = serializers.BooleanField(required=True)
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=255, required=False)
    restaurant = serializers.IntegerField(required=True)
