# Generated by Django 4.0 on 2021-12-20 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drink', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Category',
            new_name='DrinkCategory',
        ),
        migrations.RenameModel(
            old_name='Type',
            new_name='DrinkType',
        ),
    ]