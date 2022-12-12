# Generated by Django 4.0 on 2022-10-08 17:41

from django.db import migrations, models
import django.db.models.deletion
import drink.models.drink


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_remove_restaurant_picture_restaurant_picture_and_more'),
        ('drink', '0003_alter_drinkcategory_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Drink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('drinkPicture', models.ImageField(upload_to=drink.models.drink.Drink.drinks_directory_path)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_date')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_date')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.user')),
                ('drinkCategory', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='drink', to='drink.drinkcategory')),
            ],
        ),
    ]