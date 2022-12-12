from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    """Docstring for class."""

    phone = serializers.CharField(max_length=100, required=True)
    env = serializers.ChoiceField(['user', 'admin', 'livreur', 'client'])
