# Generated by Django 4.0 on 2022-08-04 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurantMenu', '0010_menu_drinks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_column='updated_date'),
        ),
        migrations.AlterField(
            model_name='publicationperiod',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_column='updated_date'),
        ),
    ]
