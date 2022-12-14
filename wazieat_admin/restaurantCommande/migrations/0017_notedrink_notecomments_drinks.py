# Generated by Django 4.0 on 2022-08-10 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurantDrink', '0006_alter_restaurantdrink_updated_at'),
        ('restaurantCommande', '0016_alter_commande_updated_at_alter_note_updated_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteDrink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, default=None, null=True)),
                ('drink', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurantDrink.restaurantdrink')),
            ],
        ),
        migrations.AddField(
            model_name='notecomments',
            name='drinks',
            field=models.ManyToManyField(to='restaurantCommande.NoteDrink'),
        ),
    ]
