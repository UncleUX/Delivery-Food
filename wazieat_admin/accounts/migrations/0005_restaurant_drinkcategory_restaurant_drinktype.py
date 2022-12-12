# Generated by Django 4.0 on 2021-12-20 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drink', '0002_rename_category_drinkcategory_rename_type_drinktype'),
        ('accounts', '0004_role_user_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='drinkCategory',
            field=models.ManyToManyField(blank=True, default=None, to='drink.DrinkCategory'),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='drinkType',
            field=models.ManyToManyField(blank=True, default=None, to='drink.DrinkType'),
        ),
    ]