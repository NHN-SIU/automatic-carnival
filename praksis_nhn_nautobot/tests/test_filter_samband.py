"""Test Samband Filter."""

from django.test import TestCase

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.tests import fixtures


class SambandFilterTestCase(TestCase):
    """Samband Filter Test Case."""

    queryset = models.Samband.objects.all()
    filterset = filters.SambandFilterSet

    @classmethod
    def setUpTestData(cls):
        """Setup test data for Samband Model."""
        fixtures.create_samband()

    def test_q_search_name(self):
        """Test using Q search with name of Samband."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for Samband."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
