# Generated by Django 4.0 on 2022-11-10 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurantCommande', '0018_notedelivery_remove_noteservice_note_livreur_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='suggestion',
            field=models.JSONField(default=None, null=True),
        ),
    ]