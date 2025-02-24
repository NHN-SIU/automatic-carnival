"""Filtering for praksis_nhn_nautobot."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from praksis_nhn_nautobot import models


class NHNModelFilterSet(NautobotFilterSet, NameSearchFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for NHNModel."""

    class Meta:
        """Meta attributes for filter."""

        model = models.NHNModel

        # add any fields from the model that you would like to filter your searches by using those
        fields = ["id", "name", "description"]
