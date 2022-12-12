# Generated by Django 4.0 on 2022-02-06 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0013_alter_module_description_alter_role_description'),
        ('restaurantFood', '0005_alter_ingredient_description_and_more'),
        ('restaurantMenu', '0008_alter_menu_description_and_more'),
        ('restaurantDrink', '0003_alter_restaurantdrink_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=6, null=True)),
                ('is_valid', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_date')),
                ('updated_at', models.DateTimeField(auto_now_add=True, db_column='updated_date')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.user')),
                ('drink', models.ManyToManyField(to='restaurantDrink.RestaurantDrink')),
                ('food', models.ManyToManyField(to='restaurantFood.RestaurantFood')),
                ('menu', models.ManyToManyField(to='restaurantMenu.Menu')),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=100)),
                ('message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_date')),
                ('updated_at', models.DateTimeField(auto_now_add=True, db_column='updated_date')),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurantCommande.commande')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.user')),
            ],
        ),
    ]