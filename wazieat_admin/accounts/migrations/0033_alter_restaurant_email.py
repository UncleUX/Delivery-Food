# Generated by Django 4.0 on 2022-11-09 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_remove_restaurant_picture_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='email',
            field=models.EmailField(default=None, max_length=255, null=True),
        ),
    ]
