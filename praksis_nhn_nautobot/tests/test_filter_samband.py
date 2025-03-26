"""Test Samband Filter."""

from django.test import TestCase

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.tests import fixtures


class SambandFilterTestCase(TestCase):
    """Samband Filter Test Case."""

    @classmethod
    def setUpTestData(cls):
        """Setup test data for Samband Model."""
        fixtures.create_samband()
        cls.filterset = filters.SambandFilterSet

    def test_filter_by_name(self):
        """Filter Samband by exact name."""
        params = {"name": "Samband One"}
        qs = self.filterset(params, models.Samband.objects.all()).qs
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "Samband One")

    def test_filter_by_status(self):
        """Filter by status 'Planned'."""
        params = {"status": "Planned"}
        qs = self.filterset(params, models.Samband.objects.all()).qs
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().status, "Planned")

    def test_filter_by_vendor(self):
        """Filter by vendor 'Telenor'."""
        params = {"vendor": "Telenor"}
        qs = self.filterset(params, models.Samband.objects.all()).qs
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().vendor, "Telenor")

    def test_filter_combination(self):
        """Filter by status + vendor."""
        params = {"status": "Active", "vendor": "Telenor"}
        qs = self.filterset(params, models.Samband.objects.all()).qs
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "Samband One")

    def test_filter_no_match(self):
        """Filter with no matching result."""
        params = {"name": "Nonexistent"}
        qs = self.filterset(params, models.Samband.objects.all()).qs
        self.assertEqual(qs.count(), 0)
