# Generated by Django 4.0 on 2022-11-10 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_alter_restaurant_email'),
        ('restaurantCommande', '0019_commande_suggestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='restaurant_suggest_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='restaurant_suggest_by', to='accounts.user'),
        ),
    ]
