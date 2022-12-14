# Generated by Django 4.0 on 2022-04-01 13:07

import accounts.models.delivery
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_restaurant_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='delivery',
            name='licence',
        ),
        migrations.RemoveField(
            model_name='delivery',
            name='year',
        ),
        migrations.AddField(
            model_name='delivery',
            name='has_motor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='delivery',
            name='has_permis',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='delivery',
            name='year_motor',
            field=models.IntegerField(choices=[(1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022)], default=accounts.models.delivery.current_year, null=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='address',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='brand',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='model',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='power',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='scan_cni',
            field=models.ImageField(null=True, upload_to=accounts.models.delivery.Delivery.delivery_directory_path),
        ),
    ]
