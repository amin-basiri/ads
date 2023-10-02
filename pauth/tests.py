from rest_framework import status
from rest_framework.test import APITestCase

from pauth import models


class SignupTest(APITestCase):

    def test_failed_required_fields_not_sent(self):
        response = self.client.post("/api/auth/sign_up/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"]["email"][0]["code"], "required")
        self.assertEqual(response.json()["detail"]["password"][0]["code"], "required")
        self.assertEqual(response.json()["detail"]["first_name"][0]["code"], "required")
        self.assertEqual(response.json()["detail"]["last_name"][0]["code"], "required")

    def test_failed_invalid_email(self):
        response = self.client.post(
            "/api/auth/sign_up/",
            {
                "email": "invalid",
                "first_name": "test",
                "last_name": "test",
                "password": "123456789"
            }
        )

        self.assertEqual(response.json()["detail"]["email"][0]["code"], "invalid")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_duplicate_email(self):
        payload = {
            "email": "test@test.com",
            "first_name": "test",
            "last_name": "test",
            "password": "123456789"
        }
        response_1 = self.client.post("/api/auth/sign_up/", payload)
        response_2 = self.client.post("/api/auth/sign_up/", payload)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_2.json()["detail"]["email"][0]["code"], "unique")

    def test_succeed_valid_data(self):
        payload = {
            "email": "test@test.com",
            "first_name": "test",
            "last_name": "test",
            "password": "123456789"
        }

        response = self.client.post("/api/auth/sign_up/", payload)

        for key, value in payload.items():
            if key != "password":
                self.assertEqual(response.json()[key], value)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SigninTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = models.PUser.objects.create_user(
            email="test@test.com",
            password="123456789",
            first_name="test",
            last_name="test"
        )

    def test_failed_invalid_email(self):
        response = self.client.post(
            "/api/auth/sign_in/",
            {
                "email": "invalid@invalid.com",
                "password": "123456789"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_failed_invalid_password(self):
        response = self.client.post(
            "/api/auth/sign_in/",
            {
                "email": "test@test.com",
                "password": "invalid"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_succeed_valid_password_email(self):
        response = self.client.post(
            "/api/auth/sign_in/",
            {
                "email": "test@test.com",
                "password": "123456789"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.json())
