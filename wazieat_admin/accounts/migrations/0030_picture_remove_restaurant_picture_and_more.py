# Generated by Django 4.0 on 2022-10-18 21:21

import accounts.models.restaurant
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_restaurant_picture_restaurant_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=accounts.models.restaurant.Picture.restaurant_picture_path)),
            ],
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='picture',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='picture_xx',
            field=models.ManyToManyField(to='accounts.Picture'),
        ),
    ]
