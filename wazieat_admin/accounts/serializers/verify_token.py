from rest_framework import serializers


class VerifyTokenSerializer(serializers.Serializer):
    """Docstring for class."""

    token = serializers.CharField()
    env = serializers.ChoiceField(['user', 'admin', 'livreur', 'client'])

