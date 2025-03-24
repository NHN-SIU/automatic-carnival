"""Forms for praksis_nhn_nautobot."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from praksis_nhn_nautobot import models


class SambandForm(NautobotModelForm):
    """NHNModel creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.Samband
        fields = [
            # Basic Information
            "name",
            "name_prefix",
            "type",
            "type_id",
            "status",
            "status_id",
            # Location Information
            "location",
            "location_id",
            "location_type",
            # Point of Presence A
            "pop_a_address_string",
            "pop_a_category",
            "pop_a_geo_string",
            "pop_a_map_url",
            "pop_a_room",
            # Point of Presence B
            "pop_b_address_string",
            "pop_b_category",
            "pop_b_geo_string",
            "pop_b_map_url",
            "pop_b_room",
            # Bandwidth Information
            "bandwidth_down",
            "bandwidth_up",
            "bandwidth_string",
            # Cost Information
            "cost_in",
            "cost_out",
            "initial_cost",
            "express_cost",
            "dekningsbidrag",
            "dekningsgrad",
            # Reference Numbers
            "sambandsnummer",
            "smbnr_nhn",
            "smbnr_orig",
            "smbnr_prefix",
            # Dates
            "order_date",
            "desired_delivery_date",
            "actually_delivery_date",
            "order_delivery_date",
            "install_date",
            "live_date",
            "start_invoice_date",
            "termination_date",
            "termination_order_date",
            # Vendor Information
            "vendor",
            "vendor_id",
            # Additional Information
            "connection_url",
            "details_included",
            "transporttype",
            "transporttype_id",
            # Relationships
            "parents",
        ]


class SambandBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    """Bulk edit form for samband"""

    pk = forms.ModelMultipleChoiceField(queryset=models.Samband.objects.all(), widget=forms.MultipleHiddenInput)

    # Fields that can be bulk edited
    status = forms.CharField(required=False)
    type = forms.CharField(required=False)
    location = forms.CharField(required=False)
    vendor = forms.CharField(required=False)
    transporttype = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "status",
            "type",
            "location",
            "vendor",
            "transporttype",
            "name_prefix",
            "pop_a_room",
            "pop_b_room",
        ]


class SambandFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.Samband
    field_order = [
        "q",
        "name",
        "status",
        "type",
        "location",
        "vendor",
        "transporttype",
    ]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name, Status, Type, Location, or Vendor.",
    )
    name = forms.CharField(required=False, label="Name")
    status = forms.CharField(required=False, label="Status")
    type = forms.CharField(required=False, label="Type")
    location = forms.CharField(required=False, label="Location")
    vendor = forms.CharField(required=False, label="Vendor")
    transporttype = forms.CharField(required=False, label="Transport Type")
