"""Create fixtures for tests."""

from praksis_nhn_nautobot.models import NHNModel


def create_nhnmodel():
    """Fixture to create necessary number of NHNModel for tests."""
    NHNModel.objects.create(name="Test One")
    NHNModel.objects.create(name="Test Two")
    NHNModel.objects.create(name="Test Three")
