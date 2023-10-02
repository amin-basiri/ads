import io
from PIL import Image

from rest_framework import status
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile

from ads import models
from pauth import models as auth_models


def _generate_photo_file():
    file = io.BytesIO()
    image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file


class BaseAdTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.settings()

        self.user = auth_models.PUser.objects.create_user(
            email="test@test.com",
            password="123456789",
            first_name="test",
            last_name="test"
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.headers = {
            "Authorization": f"token {self.token}",
        }


class CreateAdTest(BaseAdTest):
    def test_failed_required_fields_not_sent(self):
        response = self.client.post("/api/ad/", headers=self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"]["title"][0]["code"], "required")
        self.assertEqual(response.json()["detail"]["image"][0]["code"], "required")
        self.assertEqual(response.json()["detail"]["description"][0]["code"], "required")

    def test_failed_user_unauthorized(self):
        response = self.client.post("/api/ad/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_succeed_valid_data(self):
        response = self.client.post(
            "/api/ad/",
            data={
                "title": "test",
                "image": _generate_photo_file(),
                "description": "test"
            },
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ListAdTest(BaseAdTest):
    def setUp(self) -> None:
        super().setUp()

        response_1 = self.client.post(
            "/api/ad/",
            data={
                "title": "test",
                "image": _generate_photo_file(),
                "description": "test"
            },
            headers=self.headers
        )
        response_2 = self.client.post(
            "/api/ad/",
            data={
                "title": "test",
                "image": _generate_photo_file(),
                "description": "test"
            },
            headers=self.headers
        )

        self.ad_1 = models.Ads.objects.get(id=response_1.json()["id"])
        self.ad_2 = models.Ads.objects.get(id=response_2.json()["id"])

        self.comment_1 = models.Comment.objects.create(
            ads=self.ad_1,
            user=self.user,
            text="test"
        )

    def test_succeed_show_proper_date(self):
        response = self.client.get("/api/ad/")

        self.assertEqual(response.json()[0]["title"], self.ad_1.title)
        self.assertEqual(response.json()[0]["description"], self.ad_1.description)
        self.assertEqual(response.json()[0]["image"][17:], self.ad_1.image.url)
        self.assertEqual(response.json()[0]["comments"][0]["user"], f"{self.user.first_name} {self.user.last_name}")
        self.assertEqual(response.json()[0]["comments"][0]["text"], self.comment_1.text)

        self.assertEqual(response.json()[1]["title"], self.ad_2.title)
        self.assertEqual(response.json()[1]["description"], self.ad_2.description)
        self.assertEqual(response.json()[1]["image"][17:], self.ad_2.image.url)


class CommentAdTest(BaseAdTest):
    def setUp(self) -> None:
        super().setUp()

        response = self.client.post(
            "/api/ad/",
            data={
                "title": "test",
                "image": _generate_photo_file(),
                "description": "test"
            },
            headers=self.headers
        )
        self.ad = models.Ads.objects.get(id=response.json()["id"])

    def test_failed_unauthorized(self):
        response = self.client.post(
            f"/api/ad/{self.ad.id}/comment/",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_failed_ad_not_found(self):
        response = self.client.post(
            f"/api/ad/1000/comment/",
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_failed_required_fields_not_sent(self):
        response = self.client.post(
            f"/api/ad/{self.ad.id}/comment/",
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"]["text"][0]["code"], "required")

    def test_succeed_valid_data(self):

        response = self.client.post(
            f"/api/ad/{self.ad.id}/comment/",
            data={
                "text": "test"
            },
            headers=self.headers,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["user"], f"{self.user.first_name} {self.user.last_name}")
        self.assertEqual(response.json()["text"], "test")

    def test_failed_double_comment_on_same_ad(self):
        response_1 = self.client.post(
            f"/api/ad/{self.ad.id}/comment/",
            data={
                "text": "test"
            },
            headers=self.headers,
            format="json"
        )
        response_2 = self.client.post(
            f"/api/ad/{self.ad.id}/comment/",
            data={
                "text": "test",
            },
            headers=self.headers,
            format="json"
        )

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_1.json()["user"], f"{self.user.first_name} {self.user.last_name}")
        self.assertEqual(response_1.json()["text"], "test")

        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_2.json()["detail"]["non_field_errors"][0]["code"], "invalid")


class DeleteAdTest(BaseAdTest):
    def setUp(self) -> None:
        super().setUp()

        self.another_user = auth_models.PUser.objects.create_user(
            email="another_test@test.com",
            password="123456789",
            first_name="test",
            last_name="test"
        )
        self.another_token, _ = Token.objects.get_or_create(user=self.another_user)

        self.another_headers = {
            "Authorization": f"token {self.another_token}",
        }

        response = self.client.post(
            "/api/ad/",
            data={
                "title": "test",
                "image": _generate_photo_file(),
                "description": "test"
            },
            headers=self.headers
        )
        self.ad = models.Ads.objects.get(id=response.json()["id"])

    def test_failed_user_unauthorized(self):
        response = self.client.delete(f"/api/ad/{self.ad.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_failed_permission_denied(self):
        response = self.client.delete(
            f"/api/ad/{self.ad.id}/",
            headers=self.another_headers
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_failed_ad_not_found(self):
        response = self.client.delete(
            f"/api/ad/1000/",
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_succeed_valid_data(self):
        response = self.client.delete(
            f"/api/ad/{self.ad.id}/",
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Ads.objects.filter(id=self.ad.id).exists())


class UpdateAdTest(BaseAdTest):
    def setUp(self) -> None:
        super().setUp()

        self.another_user = auth_models.PUser.objects.create_user(
            email="another_test@test.com",
            password="123456789",
            first_name="test",
            last_name="test"
        )
        self.another_token, _ = Token.objects.get_or_create(user=self.another_user)

        self.another_headers = {
            "Authorization": f"token {self.another_token}",
        }

        response = self.client.post(
            "/api/ad/",
            data={
                "title": "test",
                "image": _generate_photo_file(),
                "description": "test"
            },
            headers=self.headers
        )
        self.ad = models.Ads.objects.get(id=response.json()["id"])

    def test_failed_user_unauthorized(self):
        response = self.client.patch(f"/api/ad/{self.ad.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_failed_permission_denied(self):
        response = self.client.patch(
            f"/api/ad/{self.ad.id}/",
            headers=self.another_headers
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_failed_ad_not_found(self):
        response = self.client.patch(
            f"/api/ad/1000/",
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_succeed_valid_data(self):
        payload = {
            "title": "new_test",
            "image": _generate_photo_file(),
            "description": "new_test",
        }

        response = self.client.patch(
            f"/api/ad/{self.ad.id}/",
            data=payload,
            headers=self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ad.refresh_from_db()

        self.assertEqual(self.ad.title, payload["title"])
        self.assertEqual(self.ad.description, payload["description"])
        self.assertEqual(self.ad.image.url, response.json()["image"][17:])
