from rest_framework import serializers


class ActivateFoodSerializer(serializers.Serializer):
    """Docstring for class."""

    valid_status = serializers.BooleanField()
    reason = serializers.CharField(allow_null=True, allow_blank=True, max_length=255, required=False)
