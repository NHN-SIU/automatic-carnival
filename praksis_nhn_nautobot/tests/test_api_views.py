"""Unit tests for praksis_nhn_nautobot."""

from nautobot.apps.testing import APIViewTestCases

from praksis_nhn_nautobot import models
from praksis_nhn_nautobot.tests import fixtures


class SambandAPIViewTest(APIViewTestCases.APIViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the API viewsets for Samband."""

    model = models.Samband
    create_data = [
        {
            "name": "Test Model 1",
            "description": "test description",
        },
        {
            "name": "Test Model 2",
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}

    @classmethod
    def setUpTestData(cls):
        fixtures.create_samband()
