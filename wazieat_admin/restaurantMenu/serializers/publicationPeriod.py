from rest_framework import serializers
from restaurantMenu.models.publicationPeriod import PublicationPeriod


class PublicationPeriodSerializer(serializers.ModelSerializer):
    """Docstring for class."""

    class Meta:
        """Docstring for class."""

        model = PublicationPeriod
        fields = ['id', 'name', 'reference', 'description', 'is_active',
                  'start_date', 'menu_day', 'end_date', 'repeat']
        read_only_fields = ['reference', 'is_active']
