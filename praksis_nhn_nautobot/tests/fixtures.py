"""Create fixtures for tests."""

from praksis_nhn_nautobot.models import Samband


def create_samband():
    """Fixture to create necessary number of Samband for tests."""
    Samband.objects.create(name="Test One")
    Samband.objects.create(name="Test Two")
    Samband.objects.create(name="Test Three")

    
