"""Data model that we assume in the plugin.

We assume that we know all 51 fields that come from the test data (Jinja).
"""

from django.core.validators import MinValueValidator
from django.db import models
from nautobot.apps.models import PrimaryModel
from nautobot.extras.utils import extras_features


# pylint: disable=too-many-ancestors
@extras_features("custom_fields", "custom_validators", "relationships", "graphql")
class Samband(PrimaryModel):
    """Model representing a samband."""

    # Dissable contact/team association and dynamic groups
    is_contact_associable_model = False  # Opt-out of contacts/teams UI
    is_dynamic_group_associable_model = False  # Opt-out of dynamic group filters

    # Basic Information
    name = models.CharField(max_length=100, unique=True)  # Keep this required
    name_prefix = models.CharField(max_length=10, blank=True, help_text="Prefix for the connection name")
    type = models.CharField(max_length=50, blank=True, help_text="Type of connection")
    type_id = models.IntegerField(null=True, blank=True, help_text="Identifier for connection type")
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Planned", "Planned"),
        ("Decommissioned", "Decommissioned"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, blank=True, null=False, help_text="Status of connection"
    )
    status_id = models.IntegerField(null=True, blank=True, help_text="Identifier for connection status")

    # Location Information
    location = models.CharField(max_length=100, blank=True, help_text="Physical location name")
    location_id = models.IntegerField(null=True, blank=True, help_text="Location identifier")
    location_type = models.CharField(
        max_length=50, blank=True, help_text="Type of location (e.g., Office, Data Center)"
    )

    # Point of Presence A
    pop_a_address_string = models.CharField(
        max_length=200, blank=True, help_text="Physical address of Point of Presence A"
    )
    pop_a_category = models.CharField(max_length=50, blank=True, help_text="Category of Point of Presence A")
    pop_a_geo_string = models.CharField(
        max_length=50, blank=True, help_text="Geographic coordinates of Point of Presence A"
    )
    pop_a_map_url = models.URLField(null=True, blank=True, help_text="Map URL for Point of Presence A")
    pop_a_room = models.CharField(max_length=50, blank=True, help_text="Room identifier for Point of Presence A")

    # Point of Presence B
    pop_b_address_string = models.CharField(
        max_length=200, blank=True, help_text="Physical address of Point of Presence B"
    )
    pop_b_category = models.CharField(max_length=50, blank=True, help_text="Category of Point of Presence B")
    pop_b_geo_string = models.CharField(
        max_length=50, blank=True, help_text="Geographic coordinates of Point of Presence B"
    )
    pop_b_map_url = models.URLField(null=True, blank=True, help_text="Map URL for Point of Presence B")
    pop_b_room = models.CharField(max_length=50, blank=True, help_text="Room identifier for Point of Presence B")

    # Bandwidth Information
    bandwidth_down = models.IntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True, help_text="Download bandwidth in Mbps"
    )
    bandwidth_up = models.IntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True, help_text="Upload bandwidth in Mbps"
    )
    bandwidth_string = models.CharField(
        max_length=20, blank=True, help_text="Bandwidth representation (e.g., '100 Mbps')"
    )

    # Cost Information
    cost_in = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Incoming cost amount"
    )
    cost_out = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Outgoing cost amount"
    )
    initial_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Initial setup cost"
    )
    express_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Express delivery cost"
    )
    dekningsbidrag = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Contribution margin"
    )
    dekningsgrad = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Coverage ratio in percentage"
    )

    # Reference Numbers
    sambandsnummer = models.CharField(max_length=20, unique=True, blank=True, help_text="Connection reference number")
    smbnr_nhn = models.CharField(max_length=20, unique=True, blank=True, help_text="NHN connection reference number")
    smbnr_orig = models.IntegerField(null=True, blank=True, help_text="Original connection reference number")
    smbnr_prefix = models.CharField(max_length=5, blank=True, help_text="Prefix for connection reference number")

    # Dates
    order_date = models.DateTimeField(null=True, blank=True)
    desired_delivery_date = models.DateTimeField(null=True, blank=True)
    actually_delivery_date = models.DateTimeField(null=True, blank=True)
    order_delivery_date = models.DateTimeField(null=True, blank=True)
    install_date = models.DateTimeField(null=True, blank=True)
    live_date = models.DateTimeField(null=True, blank=True)
    start_invoice_date = models.DateTimeField(null=True, blank=True)
    termination_date = models.DateTimeField(null=True, blank=True)
    termination_order_date = models.DateTimeField(null=True, blank=True)


    vendor = models.CharField(max_length=100, blank=True, help_text="Vendor providing the connection")
    vendor_id = models.IntegerField(null=True, blank=True, help_text="Identifier for the vendor")

    # Additional Information
    connection_url = models.URLField(null=True, blank=True, help_text="URL to the connection details")
    details_included = models.BooleanField(default=False)

    transporttype = models.CharField(max_length=50, blank=True, help_text="Type of transport connection")
    transporttype_id = models.IntegerField(null=True, blank=True, help_text="Identifier for transport type")

    # Relationships
    parents = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="children",
        blank=True,
        help_text="Parent connections that this connection depends on",
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name = "Samband"
        verbose_name_plural = "Samband"

    def __str__(self):
        """Stringify instance."""
        return f"{self.name}"
