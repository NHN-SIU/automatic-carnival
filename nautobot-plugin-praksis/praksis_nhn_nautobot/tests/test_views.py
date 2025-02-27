"""Unit tests for views."""

from nautobot.apps.testing import ViewTestCases

from praksis_nhn_nautobot import models
from praksis_nhn_nautobot.tests import fixtures


class SambandViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the Samband views."""

    model = models.Samband
    bulk_edit_data = {"description": "Bulk edit views"}
    form_data = {
        "name": "Test 1",
        "description": "Initial model",
    }
    csv_data = (
        "name",
        "Test csv1",
        "Test csv2",
        "Test csv3",
    )

    @classmethod
    def setUpTestData(cls):
        fixtures.create_samband()
