"""Test Samband."""

from django.test import TestCase

from praksis_nhn_nautobot import models


class TestSamband(TestCase):
    """Test Samband."""

    def test_create_samband_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        samband = models.Samband.objects.create(name="Development")
        self.assertEqual(samband.name, "Development")
        self.assertEqual(samband.description, "")
        self.assertEqual(str(samband), "Development")

    def test_create_samband_all_fields_success(self):
        """Create Samband with all fields."""
        samband = models.Samband.objects.create(name="Development", description="Development Test")
        self.assertEqual(samband.name, "Development")
        self.assertEqual(samband.description, "Development Test")
