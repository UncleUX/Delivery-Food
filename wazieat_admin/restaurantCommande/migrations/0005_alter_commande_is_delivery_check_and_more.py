# Generated by Django 4.0 on 2022-04-02 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurantCommande', '0004_alter_commande_is_delivery_check_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commande',
            name='is_delivery_check',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='commande',
            name='is_delivery_valid',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='commande',
            name='is_restaurant_valid',
            field=models.BooleanField(null=True),
        ),
    ]
