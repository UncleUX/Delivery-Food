# Generated by Django 4.0 on 2022-10-18 20:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_remove_restaurant_address_remove_restaurant_picture_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='picture_xx',
        ),
    ]
