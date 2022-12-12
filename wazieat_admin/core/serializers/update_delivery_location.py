from rest_framework import serializers


class UpdateDeliveryLocationSerializer(serializers.Serializer):
    """Docstring for class."""

    location = serializers.ListField(child=serializers.FloatField())

