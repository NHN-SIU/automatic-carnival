"""Forms for praksis_nhn_nautobot."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from praksis_nhn_nautobot import models


# pylint: disable=too-many-ancestors, nb-use-fields-all
class SambandForm(NautobotModelForm):
    """Samband creation/edit form."""

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
    """Bulk edit form for samband."""

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
    """
    Filter form to filter searches.

    Define all fields to be filtered in the "default" section (in the UI)
    """

    model = models.Samband

    name = forms.CharField(required=False, label="Name")

    type = forms.ChoiceField(required=False, label="Type")

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Any')]+models.Samband.STATUS_CHOICES,
        label="Status"
    )
    location = forms.ChoiceField(
        required=False,
        label="Location",
    )
    vendor = forms.ChoiceField(
        required=False,
        label="Vendor"
    )
    transporttype = forms.ChoiceField(
        required=False,
        label="Transport Type",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    live_date__gte = forms.DateField(
        required=False,
        label="Live Date (after or on)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    live_date__lte = forms.DateField(
        required=False,
        label="Live Date (before or on)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    termination_date__gte = forms.DateField(
        required=False,
        label="Termination Date (after or on)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    termination_date__lte = forms.DateField(
        required=False,
        label="Termination Date (before or on)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch distinct location values from the Samband model
        locations = models.Samband.objects.values_list('location', flat=True)
        vendors = models.Samband.objects.values_list('vendor', flat=True).distinct()
        transporttypes = models.Samband.objects.values_list('transporttype', flat=True).distinct()
        types = models.Samband.objects.values_list('type', flat=True).distinct()
        location_choices =          sorted([('', 'Any')] + [(loc, loc) for loc in set(locations) if loc])
        vendor_choices =            sorted([('', 'Any')] + [(ven, ven) for ven in set(vendors) if ven])
        transporttype_choices =     sorted([('', 'Any')] + [(tpt, tpt) for tpt in set(transporttypes) if tpt])
        type_choices =              sorted([('', 'Any')] + [(tpt, tpt) for tpt in set(types) if tpt])
        self.fields['location'].choices = location_choices
        self.fields['vendor'].choices = vendor_choices
        self.fields['transporttype'].choices = transporttype_choices
        self.fields['type'].choices = type_choices
        