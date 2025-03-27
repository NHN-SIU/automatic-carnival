# """Tables for praksis_nhn_nautobot."""

# import django_tables2 as tables
# from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn

# from praksis_nhn_nautobot import models


# class SambandTable(BaseTable):
#     # pylint: disable=R0903
#     """Table for list view."""

#     pk = ToggleColumn()
#     name = tables.Column(linkify=True)
#     actions = ButtonsColumn(
#         models.Samband,
#         # Option for modifying the default action buttons on each row:
#         buttons=("changelog", "edit", "delete"),
        
#         # Option for modifying the pk for the action buttons:
#         pk_field="pk",
#     )

#     class Meta(BaseTable.Meta):
#         """Meta attributes."""

#         model = models.Samband
#         fields = (
#             "pk",
#             "name",
#         )

#         # Option for modifying the columns that show up in the list view by default:
#         default_columns = (
#             "pk",
#             "name",
#         )


"""Tables for praksis_nhn_nautobot."""

import django_tables2 as tables
from django_tables2.columns import TemplateColumn
from django.urls import reverse
from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn

from praksis_nhn_nautobot import models


class SambandTable(BaseTable):
    # pylint: disable=R0903
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    status = TemplateColumn(
        template_code="""
            {% with record.status|lower as status %}
                {% if status == "active" %}
                    <span class="badge" style="background-color: #23d217; color: white;">{{ record.status }}</span>
                {% elif status == "planned" %}
                    <span class="badge" style="background-color: #58aef9; color: white;">{{ record.status }}</span>
                {% elif status == "decommissioned" %}
                    <span class="badge" style="background-color: #e31313; color: white;">{{ record.status }}</span>
                {% else %}
                    <span class="badge" style="background-color: gray; color: white;">{{ record.status }}</span>
                {% endif %}
            {% endwith %}
        """,
        verbose_name="Status",
        orderable=True,
    )

    location = tables.Column()
    type = tables.Column()
    location_type = tables.Column()
    vendor = tables.Column()
    transporttype = tables.Column()
    parents = TemplateColumn(
        template_code="""
            {% for parent in record.parents.all %}
                <a href="{{ parent.get_absolute_url }}">{{ parent.name }}</a>{% if not forloop.last %}, {% endif %}
            {% empty %}
                <span class="text-muted">None</span>
            {% endfor %}
        """,
        orderable=True,
        verbose_name="Parent",
    )

    graph = tables.TemplateColumn(
        template_code="""
        <a href="{% url 'plugins:praksis_nhn_nautobot:samband_graph' record.pk %}" class="btn btn-sm btn-primary" title="View Graph">
            <i class="mdi mdi-graph"></i>
        </a>
        """,
        orderable=False,
        verbose_name="Graph"
    )
    
    # Add a custom map button column
    map = tables.TemplateColumn(
        template_code="""
        <a href="{% url 'plugins:praksis_nhn_nautobot:samband_map' record.pk %}" class="btn btn-sm btn-primary" title="View Map">
            <i class="mdi mdi-map-marker"></i>
        </a>
        """,
        orderable=False,
        verbose_name="Map"
    )
    
    actions = ButtonsColumn(
        models.Samband,
        # Option for modifying the default action buttons on each row:
        buttons=("changelog", "edit", "delete"),
        # Option for modifying the pk for the action buttons:
        pk_field="pk",
    )


    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.Samband
        fields = (
            "name",
            "status",
            "location",
            "location_type",
            "type",
            "vendor",
            "transporttype",
            "parents",
            # "map",
            # "graph",
            "map",
            "actions",
        )
