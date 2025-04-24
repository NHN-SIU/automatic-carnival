"""Filtering for praksis_nhn_nautobot."""

import django_filters
from django.db.models import Q
from nautobot.apps.filters import NautobotFilterSet

from praksis_nhn_nautobot.models import Samband


# pylint: disable=nb-use-fields-all
class SambandFilterSet(NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for Samband."""

    # Filter for search bar
    q = django_filters.CharFilter(
        method="filter_q",
        label="Search",
    )

    # Dropdown/multi-choice filters for discrete fields:
    status = django_filters.MultipleChoiceFilter(choices=Samband.STATUS_CHOICES, label="Status")
    vendor = django_filters.CharFilter(label="Vendor")
    transporttype = django_filters.CharFilter(label="Transport Type")
    location = django_filters.CharFilter(label="Location")
    type = django_filters.CharFilter(label="Type")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains", label="Name (contains)")

    # Date range filters (greater-than or equal and less-than or equal):
    live_date__gte = django_filters.DateFilter(
        field_name="live_date", lookup_expr="gte", label="Live Date (after or on)"
    )
    live_date__lte = django_filters.DateFilter(
        field_name="live_date", lookup_expr="lte", label="Live Date (before or on)"
    )
    termination_date__gte = django_filters.DateFilter(
        field_name="termination_date", lookup_expr="gte", label="Termination Date (after or on)"
    )
    termination_date__lte = django_filters.DateFilter(
        field_name="termination_date", lookup_expr="lte", label="Termination Date (before or on)"
    )

    class Meta:
        """Meta attributes for filter."""

        model = Samband

        # Include filter fields in Meta so Nautobot knows which ones to expose.
        fields = "__all__"

        # Can also use fields = "__all___" in combination with exclude = [] to exclude specific fields

    def filter_q(self, queryset, name, value):
        """Filter for search bar.

        This filter allows searching across multiple fields in the model.
        """
        return queryset.filter(Q(name__icontains=value) | Q(location__icontains=value) | Q(vendor__icontains=value))
