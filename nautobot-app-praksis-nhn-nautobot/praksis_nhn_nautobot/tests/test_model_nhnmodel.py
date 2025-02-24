"""Test NHNModel."""

from django.test import TestCase

from praksis_nhn_nautobot import models


class TestNHNModel(TestCase):
    """Test NHNModel."""

    def test_create_nhnmodel_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        nhnmodel = models.NHNModel.objects.create(name="Development")
        self.assertEqual(nhnmodel.name, "Development")
        self.assertEqual(nhnmodel.description, "")
        self.assertEqual(str(nhnmodel), "Development")

    def test_create_nhnmodel_all_fields_success(self):
        """Create NHNModel with all fields."""
        nhnmodel = models.NHNModel.objects.create(name="Development", description="Development Test")
        self.assertEqual(nhnmodel.name, "Development")
        self.assertEqual(nhnmodel.description, "Development Test")
