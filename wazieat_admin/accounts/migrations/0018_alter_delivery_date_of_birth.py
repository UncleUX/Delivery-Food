# Generated by Django 4.0 on 2022-05-31 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_delivery_scan_cni_alter_delivery_year_motor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='date_of_birth',
            field=models.DateField(),
        ),
    ]
