# Generated by Django 4.0 on 2022-07-30 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_alter_delivery_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
