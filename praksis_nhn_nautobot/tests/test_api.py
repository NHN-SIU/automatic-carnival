"""Unit tests for praksis_nhn_nautobot."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from nautobot.users.models import Token
from rest_framework import status
from rest_framework.test import APIClient

from praksis_nhn_nautobot.models import Samband

User = get_user_model()


class BaseAPITestCase(TestCase):
    """Base class for Praksis NHN Nautobot API tests."""

    def setUp(self):
        """Set up a test superuser and API token."""
        self.user = User.objects.create_superuser(
            username="testuser", email="test@example.com", password="securepass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_placeholder(self):
        """Verify that devices can be listed."""
        url = reverse("dcim-api:device-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


class SambandAPITest(BaseAPITestCase):
    """Test Samband API endpoints."""

    def setUp(self):
        super().setUp()
        self.samband = Samband.objects.create(name="Test Samband", sambandsnummer="SB001", smbnr_nhn="NHN001")

    def test_list_samband(self):
        """Test that we can list Samband via the API."""
        url = reverse("plugins-api:praksis_nhn_nautobot-api:samband-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_samband(self):
        """Test that we can create a Samband via the API."""
        url = reverse("plugins-api:praksis_nhn_nautobot-api:samband-list")
        payload = {
            "name": "API Created",
            "sambandsnummer": "SB999",
            "smbnr_nhn": "NHN999",
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Samband.objects.filter(name="API Created").exists())
