from rest_framework import serializers

TYPE_CHOICES = (
    (1, "restaurant"),
    (2, "livreur"),
)


class AdminValidateSerializer(serializers.Serializer):
    """Docstring for class."""

    activate_reason = serializers.CharField(max_length=255, allow_null=True)
    activate_status = serializers.BooleanField()
    type_account = serializers.ChoiceField(choices=TYPE_CHOICES)
    object_id = serializers.IntegerField()



