# Generated by Django 4.0 on 2022-10-08 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drink', '0004_drink'),
        ('restaurantDrink', '0006_alter_restaurantdrink_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurantdrink',
            name='admin_drink',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='drink.drink'),
        ),
    ]