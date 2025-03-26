"""Create fixtures for tests."""

from praksis_nhn_nautobot.models import Samband


def create_samband():
    """Fixture to create multiple unique Samband instances for testing."""
    Samband.objects.create(
        name="Samband One",
        sambandsnummer="SB001",
        smbnr_nhn="NHN001",
        status="Active",
        vendor="Telenor",
        transporttype="Fiber",
    )

    Samband.objects.create(
        name="Samband Two",
        sambandsnummer="SB002",
        smbnr_nhn="NHN002",
        status="Planned",
        vendor="GlobalConnect",
        transporttype="Microwave",
    )

    Samband.objects.create(
        name="Samband Three",
        sambandsnummer="SB003",
        smbnr_nhn="NHN003",
        status="Decommissioned",
        vendor="Telia",
        transporttype="Fiber",
    )
