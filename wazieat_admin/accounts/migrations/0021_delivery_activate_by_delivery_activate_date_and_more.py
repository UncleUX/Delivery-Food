# Generated by Django 4.0 on 2022-07-30 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_restaurant_activate_by_restaurant_activate_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='activate_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='delivery_activate_by', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='delivery',
            name='activate_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='delivery',
            name='activate_reason',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='activate_reason',
            field=models.TextField(default=None, null=True),
        ),
    ]