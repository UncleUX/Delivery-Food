# Generated by Django 4.0 on 2021-12-23 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0002_foodtype'),
        ('accounts', '0010_user_is_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='foodType',
            field=models.ManyToManyField(blank=True, default=None, to='food.FoodType'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='module',
            field=models.ManyToManyField(default=None, to='accounts.Module'),
        ),
    ]
