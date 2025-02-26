"""Tables for praksis_nhn_nautobot."""

import django_tables2 as tables
from django.urls import reverse
from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn

from praksis_nhn_nautobot import models


class NHNModelTable(BaseTable):
    # pylint: disable=R0903
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    status = tables.Column()
    location = tables.Column()
    bandwidth_string = tables.Column(verbose_name="Bandwidth")
    sambandsnummer = tables.Column(verbose_name="Connection ID")
    actions = ButtonsColumn(
        models.NHNModel,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        pk_field="pk",
    )

    # Add a custom graph button column
    graph = tables.TemplateColumn(
        template_code="""
        <a href="{% url 'plugins:praksis_nhn_nautobot:nhnmodel_graph' record.pk %}" class="btn btn-sm btn-primary" title="View Graph">
            <i class="mdi mdi-graph"></i>
        </a>
        """,
        verbose_name="Graph"
    )

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.NHNModel
        fields = (
            "pk",
            "name",
            "status",
            "location",
            "bandwidth_string",
            "sambandsnummer",
            "parents",
            "actions"
        )

        # Option for modifying the columns that show up in the list view by default:
        default_columns = (
            "pk",
            "name",
            "status",
            "location",
            "bandwidth_string",
            "sambandsnummer",
            "parents",
            "actions"
        )

        # Explicitly exclude fields
        exclude = ("dynamic_groups",)