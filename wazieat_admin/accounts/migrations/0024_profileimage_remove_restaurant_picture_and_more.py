# Generated by Django 4.0 on 2022-08-12 23:53

import accounts.models.restaurant
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_user_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField()),
            ],
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='picture',
            field=models.ManyToManyField(related_name='picture', to='accounts.ProfileImage'),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='profile_picture',
            field=models.ManyToManyField(related_name='profile_picture', to='accounts.ProfileImage'),
        ),
    ]
