from django.test import SimpleTestCase
from django.urls import reverse, resolve
import drink
import json


class TestUrls(SimpleTestCase):

    def test_list_url_is_resolved(self):
        url = reverse('api:drink_type-list')
        response = self.client.get(url, HTTP_ACCEPT='application/json')
        view = drink.views.type.DrinkTypeViewSet.as_view({'get': 'list'})
        self.assertEquals(response.resolver_match.func.__name__, view.__name__)

    def test_detail_url_is_resolved(self):
        url = reverse('api:drink_type-detail', kwargs={'pk': 1})
        response = self.client.get(url, HTTP_ACCEPT='application/json')
        view = drink.views.type.DrinkTypeViewSet.as_view({'get': 'retrieve'})
        self.assertEquals(response.resolver_match.func.__name__, view.__name__)

    def test_create_url_is_resolved(self):
        url = reverse('api:drink_type-list')
        data = {}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        view = drink.views.type.DrinkTypeViewSet.as_view({'post': 'create'})
        self.assertEquals(response.resolver_match.func.__name__, view.__name__)

    def test_update_url_is_resolved(self):
        url = reverse('api:drink_type-list')
        data = {}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        view = drink.views.type.DrinkTypeViewSet.as_view({'put': 'update'})
        self.assertEquals(response.resolver_match.func.__name__, view.__name__)

    def test_update_url_is_resolved(self):
        url = reverse('api:drink_type-list')
        data = {}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        view = drink.views.type.DrinkTypeViewSet.as_view({'put': 'update'})
        self.assertEquals(response.resolver_match.func.__name__, view.__name__)
