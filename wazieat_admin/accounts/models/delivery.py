from django.db import models
import datetime
import hashlib
from django.contrib.postgres.fields import ArrayField


def current_year():
    return datetime.date.today().year


def year_choices():
    return [(r, r) for r in range(1969, datetime.date.today().year + 1)]


year_choice = year_choices()


class Delivery(models.Model):

    def delivery_directory_path(self, filename):
        """Docstring for function."""
        time = datetime.datetime.now().isoformat()
        plain = str(self.date_of_birth) + '\0' + time
        return 'Delivery/{0}/{1}'.format(
            hashlib.sha1(
                plain.encode('utf-8')
            ).hexdigest(),
            filename)

    date_of_birth = models.DateField()
    scan_cni = models.ImageField(upload_to=delivery_directory_path, default=None)
    address = models.CharField(max_length=255)
    has_permis = models.BooleanField(default=False)
    has_motor = models.BooleanField(default=False)
    brand = models.CharField(max_length=255, null=True, default=None)
    model = models.CharField(max_length=255, null=True, default=None)
    power = models.CharField(max_length=255, null=True, default=None)
    year_motor = models.IntegerField(choices=year_choice, default=None, null=True)
    activate_date = models.DateTimeField(null=True, default=None)
    activate_reason = models.TextField(default=None, null=True)
    activate_by = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        null=True,
        default=None,
        related_name='delivery_activate_by'
    )
    location = ArrayField(
        models.FloatField(default=0),
        size=2, null=True, default=None
    )

