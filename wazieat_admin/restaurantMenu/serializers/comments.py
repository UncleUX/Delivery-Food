from rest_framework import serializers
from accounts.models.user import User
from restaurantMenu.models.menu import Menu
from restaurantMenu.models.comments import Comments


class CommentsSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    menu = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        """Docstring for class."""

        model = Comments
        fields = ['id', 'client', 'reference', 'comment', 'created_at',
                  'updated_at', 'menu']
        read_only_fields = ['reference', 'created_at', 'updated_at', 'client']


class CommentsCreateSerializer(serializers.Serializer):
    """Docstring for class."""

    menu = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all().filter(
            is_active=True,
            is_deleted=False
        ),
        required=True,
        allow_null=False,
        allow_empty=False
    )
    restaurant = serializers.IntegerField(required=True)
    comment = serializers.CharField(required=True)

