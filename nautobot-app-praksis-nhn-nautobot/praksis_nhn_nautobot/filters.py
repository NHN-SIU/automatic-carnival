"""Filtering for praksis_nhn_nautobot."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from praksis_nhn_nautobot import models


class NHNModelFilterSet(NautobotFilterSet, NameSearchFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for NHNModel."""

    class Meta:
        """Meta attributes for filter."""

        model = models.NHNModel

        # add any fields from the model that you would like to filter your searches by using those
        fields = ['actually_delivery_date', 'bandwidth_down', 'bandwidth_string', 'bandwidth_up', 'connection_url', 'cost_in', 'cost_out', 'dekningsbidrag', 'dekningsgrad', 'desired_delivery_date', 'details_included', 'express_cost', 'id', 'initial_cost', 'install_date', 'live_date', 'location', 'location_id', 'location_type', 'name', 'name_prefix', 'order_date', 'order_delivery_date', 'parents', 'pop_a_address_string', 'pop_a_category', 'pop_a_geo_string', 'pop_a_map_url', 'pop_a_room', 'pop_b_address_string', 'pop_b_category', 'pop_b_geo_string', 'pop_b_map_url', 'pop_b_room', 'sambandsnummer', 'smbnr_nhn', 'smbnr_orig', 'smbnr_prefix', 'start_invoice_date', 'status', 'status_id', 'termination_date', 'termination_order_date', 'transporttype', 'transporttype_id', 'type', 'type_id', 'vendor', 'vendor_id']
