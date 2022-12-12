from django.test import SimpleTestCase
from django_tenants.test.cases import TenantTestCase
from django.test.utils import override_settings


class TestUrls(TenantTestCase):

    @override_settings(ROOT_URLCONF='wazieats.urls')
    def test_login_url_is_resolved(self):
        assert 1 == 2
