# Generated by Django 4.0 on 2021-12-20 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0001_initial'),
        ('accounts', '0005_restaurant_drinkcategory_restaurant_drinktype'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='foodCategory',
            field=models.ManyToManyField(blank=True, default=None, to='food.FoodCategory'),
        ),
    ]
