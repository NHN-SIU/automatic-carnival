"""Unit tests for views."""

from nautobot.core.testing import ViewTestCases

from praksis_nhn_nautobot.models import Samband


class SambandUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Samband UI views."""

    model = Samband
    bulk_edit_url_name = "plugins:praksis_nhn_nautobot:samband_bulk_edit"
    bulk_delete_url_name = "plugins:praksis_nhn_nautobot:samband_bulk_delete"
    list_url_name = "plugins:praksis_nhn_nautobot:samband_list"
    add_url_name = "plugins:praksis_nhn_nautobot:samband_add"
    edit_url_name = "plugins:praksis_nhn_nautobot:samband_edit"
    detail_url_name = "plugins:praksis_nhn_nautobot:samband"
    delete_url_name = "plugins:praksis_nhn_nautobot:samband_delete"

    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            "name": "Test Samband",
            "sambandsnummer": "SB001",
            "smbnr_nhn": "NHN001",
            "status": "Active",
            "vendor": "Telenor",
            "transporttype": "Fiber",
        }

        cls.bulk_edit_data = {
            "status": "Planned",
            "vendor": "Telia",
            "transporttype": "Fiber",
        }

        # Create two Samband objects
        cls.model.objects.create(
            name="Existing Samband 1",
            sambandsnummer="SB999",
            smbnr_nhn="NHN999",
            status="Active",
            vendor="Broadnet",
            transporttype="Microwave",
        )

        cls.model.objects.create(
            name="Existing Samband 2",
            sambandsnummer="SB998",
            smbnr_nhn="NHN998",
            status="Planned",
            vendor="Telenor",
            transporttype="Fiber",
        )

        cls.model.objects.create(
            name="Existing Samband 3",
            sambandsnummer="SB997",
            smbnr_nhn="NHN997",
            status="Planned",
            vendor="Telia",
            transporttype="Fiber",
        )

        cls.model.objects.create(
            name="Existing Samband 4",
            sambandsnummer="SB996",
            smbnr_nhn="NHN996",
            status="Decommissioned",
            vendor="Telenor",
            transporttype="Fiber",
        )

        cls.model.objects.create(
            name="Existing Samband 5",
            sambandsnummer="SB995",
            smbnr_nhn="NHN995",
            status="Active",
            vendor="GlobalConnect",
            transporttype="Microwave",
        )

        cls.model.objects.create(
            name="Existing Samband 6",
            sambandsnummer="SB994",
            smbnr_nhn="NHN994",
            status="Planned",
            vendor="Telia",
            transporttype="Fiber",
        )
