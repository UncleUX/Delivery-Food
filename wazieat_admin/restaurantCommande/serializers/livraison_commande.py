from rest_framework import serializers


class LivraisonCommandeSerializer(serializers.Serializer):
    """Docstring for class."""

    code = serializers.CharField(allow_null=True, allow_blank=True, max_length=255)
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=255, required=False)


class LivraisonCreateCommandeSerializer(serializers.Serializer):
    """Docstring for class."""

    code = serializers.CharField(allow_null=True, allow_blank=True, max_length=255)
    message = serializers.CharField(allow_null=False, allow_blank=False, max_length=255, required=False)
    restaurant = serializers.IntegerField(required=True)
