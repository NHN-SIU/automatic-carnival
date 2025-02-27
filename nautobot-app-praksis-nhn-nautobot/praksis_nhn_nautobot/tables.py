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

    status = tables.TemplateColumn(
        template_code="""
        {% if record.status == 'Active' %}
            <span class="label label-success">Active</span>
        {% elif record.status == 'planned' %}
            <span class="label label-info">Planned</span>
        {% elif record.status == 'offline' %}
            <span class="label label-danger">Offline</span>
        {% elif record.status == 'maintenance' %}
            <span class="label label-warning">Maintenance</span>
        {% else %}
            <span class="label label-default">{{ record.status }}</span>
        {% endif %}
        """,
        verbose_name="Status"
    )
    
    location = tables.Column()
    bandwidth_string = tables.Column(verbose_name="Bandwidth")
    sambandsnummer = tables.Column(verbose_name="Connection ID")
    
    # Custom template for parent connections with badges
    parents = tables.TemplateColumn(
        template_code="""
        {% for parent in record.parents.all %}
            <a href="{% url 'plugins:praksis_nhn_nautobot:nhnmodel' parent.pk %}" class="label label-primary">
                {{ parent }}
            </a>
            {% if not forloop.last %}&nbsp;{% endif %}
        {% empty %}
            <span class="text-muted">None</span>
        {% endfor %}
        """,
        verbose_name="Parent Connections"
    )
    
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
            "graph",
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
            "graph",
            "actions"
        )

        # Explicitly exclude fields
        exclude = ("dynamic_groups",)