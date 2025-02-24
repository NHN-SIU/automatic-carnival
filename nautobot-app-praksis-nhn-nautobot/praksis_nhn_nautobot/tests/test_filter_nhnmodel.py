"""Test NHNModel Filter."""

from django.test import TestCase

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.tests import fixtures


class NHNModelFilterTestCase(TestCase):
    """NHNModel Filter Test Case."""

    queryset = models.NHNModel.objects.all()
    filterset = filters.NHNModelFilterSet

    @classmethod
    def setUpTestData(cls):
        """Setup test data for NHNModel Model."""
        fixtures.create_nhnmodel()

    def test_q_search_name(self):
        """Test using Q search with name of NHNModel."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for NHNModel."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
