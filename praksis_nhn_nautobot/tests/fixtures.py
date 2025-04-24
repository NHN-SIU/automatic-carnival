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


def create_n_samband(n=20):
    """Create n unique Samband instances for testing."""
    statuses = ["Active", "Planned", "Decommissioned"]
    vendors = ["Telenor", "Telia", "GlobalConnect", "Altibox"]
    transport_types = ["Fiber", "Microwave", "5G", "DSL"]

    for i in range(n):
        Samband.objects.create(
            name=f"Samband {i+1}",
            sambandsnummer=f"SB{i+1:03}",
            smbnr_nhn=f"NHN{i+1:03}",
            status=statuses[i % len(statuses)],
            vendor=vendors[i % len(vendors)],
            transporttype=transport_types[i % len(transport_types)],
        )