from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class BaseUserTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="admin12345"
        )
        self.regular_user = User.objects.create_user(
            username="user1", password="user12345"
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)


class UserViewSetTest(BaseUserTestCase):
    def test_register_user_with_duplicate_username_should_fail(self):
        url = "/users/"

        data = {
            "username": "user1",
            "password": "StrongPass123",
            "password2": "StrongPass123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
