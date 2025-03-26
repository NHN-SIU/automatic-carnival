"""Filtering for praksis_nhn_nautobot."""

import django_filters
from nautobot.apps.filters import NautobotFilterSet

from praksis_nhn_nautobot import models


# pylint: disable=nb-use-fields-all
class SambandFilterSet(NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for Samband."""

    status = django_filters.CharFilter(lookup_expr="exact")
    vendor = django_filters.CharFilter(lookup_expr="exact")

    class Meta:
        """Meta attributes for filter."""

        model = models.Samband

        # add any fields from the model that you would like to filter in the "advanced"  filter
        fields = "__all__"

        # Can also use fields = "__all___" in combination with exclude = [] to exclude specific fields
