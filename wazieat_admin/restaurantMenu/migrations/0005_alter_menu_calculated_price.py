# Generated by Django 4.0 on 2022-02-01 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurantMenu', '0004_alter_menu_percent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='calculated_price',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=6),
        ),
    ]