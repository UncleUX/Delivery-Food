# Generated by Django 4.0 on 2022-10-18 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0030_picture_remove_restaurant_picture_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='restaurant',
            old_name='picture_xx',
            new_name='picture',
        ),
    ]
