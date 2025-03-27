"""Test Samband."""

from django.test import TestCase

from praksis_nhn_nautobot.models import Samband


class SambandModelTest(TestCase):
    """Tests for the Samband model."""

    def setUp(self):
        """Create a basic Samband object for use in tests."""
        self.samband = Samband.objects.create(
            name="Test Samband",
            sambandsnummer="SB001",
            smbnr_nhn="NHN001",
            status="Active",
            vendor="Telenor",
            transporttype="Fiber",
        )

    def test_object_created(self):
        """Test that the Samband object is created properly."""
        self.assertEqual(Samband.objects.count(), 1)
        self.assertEqual(self.samband.name, "Test Samband")

    def test_str_representation(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.samband), "Test Samband")

    def test_unique_constraints(self):
        """Test that name and sambandsnummer must be unique."""
        with self.assertRaises(Exception):  # IntegrityError wrapped by Django
            Samband.objects.create(
                name="Test Samband",  # Duplicate name
                sambandsnummer="SB001",  # Duplicate sambandsnummer
                smbnr_nhn="NHN001",  # Also unique
            )

    def test_optional_fields_blank(self):
        """Test that optional fields can be left blank or null."""
        samband = Samband.objects.create(name="Blank Test", sambandsnummer="SB002", smbnr_nhn="NHN002")
        self.assertEqual(samband.status, "")
        self.assertEqual(samband.vendor, "")
        self.assertEqual(samband.transporttype, "")
