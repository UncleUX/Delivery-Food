from django.test import TestCase
from accounts.models.user import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from drink.models.category import DrinkCategory
from drink.models.type import DrinkType
from rest_framework.authtoken.models import Token
import json


class ReadDrinkTypeTest(APITestCase):
    def setUp(self):
        # Get urls
        self.list_url = reverse('api:drink_type-list')
        self.detail_url = reverse('api:drink_type-detail', kwargs={'pk': 2})
        self.token = None

        # Create admin user and authorization
        user = User.objects.create_superuser(email="admin@local.com", password="superadmin", phone="+45654334876", last_name="Admin", first_name="Admin")
        self.token, created = Token.objects.get_or_create(user=user)
        self.token.save()
        self.client.credentials(HTTP_AUTHORIZATION='token ' + str(self.token.key))

    def test_drink_type_list(self):
        self.type = DrinkType.objects.create(name="Pepperoni Pizza", description="It's rounded")
        DrinkType.objects.create(name="Beef Ragu", description="It's moo'")
        response = self.client.get(self.list_url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual("application/json", response['Content-Type'])

    def test_drink_type_list_not_allowed(self):
        self.type = DrinkType.objects.create(name="Pepperoni Pizza", description="It's rounded")
        DrinkType.objects.create(name="Beef Ragu", description="It's moo'")
        response = self.client.post(self.detail_url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_drink_type_detail(self):
        self.type = DrinkType.objects.create(name="Pepperoni Pizza", description="It's rounded")
        response = self.client.get(self.detail_url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.type.name)
        self.assertEqual("application/json", response['Content-Type'])


class CreateDrinkTypeTest(APITestCase):
    def setUp(self):
        # Get urls
        self.list_url = reverse('api:drink_type-list')
        self.detail_url = reverse('api:drink_type-detail', kwargs={'pk': 1})
        self.token = None

        # Create admin user and authorization
        user = User.objects.create_superuser(email="admin@local.com", password="superadmin", phone="+45654334876", last_name="Admin", first_name="Admin")
        self.token, created = Token.objects.get_or_create(user=user)
        self.token.save()
        self.client.credentials(HTTP_AUTHORIZATION='token ' + str(self.token.key))

    def test_drink_type_create(self):
        data = {"name": "type1", "description": "Hello"}
        response = self.client.post(path=self.list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual("application/json", response['Content-Type'])

    def test_drink_type_create_not_allowed(self):
        response = self.client.post(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_drink_type_create_no_data(self):
        data = {}
        response = self.client.post(path=self.list_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)


class UpdateDrinkTypeTest(APITestCase):
    def setUp(self):
        # Get urls
        self.list_url = reverse('api:drink_type-list')
        self.detail_url = reverse('api:drink_type-detail', kwargs={'pk': 1})
        self.token = None

        # Create admin user and authorization
        user = User.objects.create_superuser(email="admin@local.com", password="superadmin", phone="+45654334876", last_name="Admin", first_name="Admin")
        self.token, created = Token.objects.get_or_create(user=user)
        self.token.save()
        self.client.credentials(HTTP_AUTHORIZATION='token ' + str(self.token.key))

    def test_drink_type_update_not_allowed(self):
        response = self.client.put(reverse('api:drink_type-list'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DeleteDrinkTypeTest(APITestCase):
    def setUp(self):
        # Get urls
        self.list_url = reverse('api:drink_type-list')
        self.detail_url = reverse('api:drink_type-detail', kwargs={'pk': 1})
        self.token = None

        # Create admin user and authorization
        user = User.objects.create_superuser(email="admin@local.com", password="superadmin", phone="+45654334876", last_name="Admin", first_name="Admin")
        self.token, created = Token.objects.get_or_create(user=user)
        self.token.save()
        self.client.credentials(HTTP_AUTHORIZATION='token ' + str(self.token.key))

    def test_drink_type_delete_not_allowed(self):
        response = self.client.delete(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
