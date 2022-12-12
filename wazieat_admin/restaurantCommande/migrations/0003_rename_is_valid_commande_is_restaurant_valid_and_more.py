# Generated by Django 4.0 on 2022-04-02 16:47

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_delivery_location'),
        ('restaurantCommande', '0002_commande_cancel_validation_by_commande_validated_by_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commande',
            old_name='is_valid',
            new_name='is_restaurant_valid',
        ),
        migrations.RemoveField(
            model_name='commande',
            name='cancel_validation_by',
        ),
        migrations.RemoveField(
            model_name='commande',
            name='validated_by',
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_cancel_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_cancel_validated_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='delivery_cancel_validated_by', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_check_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_location',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(default=0), default=None, null=True, size=2),
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_validate_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_validated_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='delivery_validated_by', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='commande',
            name='is_delivery_check',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commande',
            name='is_delivery_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commande',
            name='restaurant_cancel_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='restaurant_cancel_validated_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='restaurant_cancel_validation_user', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='commande',
            name='restaurant_validate_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='restaurant_validated_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='restaurant_validated_by', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='commande',
            name='status',
            field=models.IntegerField(choices=[(1, 'Enregistrée'), (2, 'Validée par le livreur'), (3, 'En cours de préparation'), (4, 'En cours de livraison'), (5, 'Livrée'), (6, 'Annulée')], default=1),
        ),
        migrations.AddField(
            model_name='commande',
            name='token',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
