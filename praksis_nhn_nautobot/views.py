"""Views for praksis_nhn_nautobot."""

from nautobot.apps.views import NautobotUIViewSet
from nautobot.apps.ui import SectionChoices, ObjectFieldsPanel, ObjectDetailContent, Button, DropdownButton
from nautobot.core.views import generic
from nautobot.core.choices import ButtonColorChoices
from django.views.generic import DetailView, View, TemplateView
from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.http import urlencode
from django.db.models import Q  # Import Q from django.db.models

from praksis_nhn_nautobot.api.serializers import SambandSerializer
from praksis_nhn_nautobot.services.graph_service import SambandGraphService
from praksis_nhn_nautobot import filters, forms, models, tables
from praksis_nhn_nautobot.api import serializers
from praksis_nhn_nautobot.services.graph_service import SambandGraphService

from math import radians, cos, sin, asin, sqrt
from .models import Samband



class SambandUIViewSet(NautobotUIViewSet):
    """
    NautobotUIViewSet allows us to modify the existing UI of Nautobot by extending built-in views with custom forms, filters, tables, and templates.

    This viewset defines the user interface
    for interacting with Samband objects, including listing, creating, editing, and deleting entries.
    It uses custom forms for single and bulk editing, a filterset for list filtering, a serializer
    for API support, and a table definition for how Samband objects are displayed in the list view.
    For more info, check out:
    https://docs.nautobot.com/projects/core/en/stable/development/apps/api/views/nautobotuiviewset/
    """

    bulk_update_form_class = forms.SambandBulkEditForm
    filterset_class = filters.SambandFilterSet
    filterset_form_class = forms.SambandFilterForm
    form_class = forms.SambandForm
    lookup_field = "pk"
    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    table_class = tables.SambandTable

    # Resource for ObjectDetailContent:
    #https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/#basic-setup
    object_detail_content = ObjectDetailContent(
        panels = [
            # 🧩 Basic Info
            ObjectFieldsPanel(
                label="Basic Information",
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "name", "name_prefix", "type", "type_id", "status", "status_id",
                ],
            ),

            # 📍 Location Info
            ObjectFieldsPanel(
                label="Location",
                weight=110,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "location", "location_id", "location_type",
                ],
            ),

            # 📦 Point of Presence A
            ObjectFieldsPanel(
                label="Point of Presence A",
                weight=120,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "pop_a_address_string", "pop_a_category", "pop_a_geo_string",
                    "pop_a_map_url", "pop_a_room",
                ],
            ),

            # 📦 Point of Presence B
            ObjectFieldsPanel(
                label="Point of Presence B",
                weight=130,
                section=SectionChoices.LEFT_HALF,
                fields=[
                    "pop_b_address_string", "pop_b_category", "pop_b_geo_string",
                    "pop_b_map_url", "pop_b_room",
                ],
            ),

            # 📶 Bandwidth
            ObjectFieldsPanel(
                label="Bandwidth",
                weight=140,
                section=SectionChoices.RIGHT_HALF,
                fields=[
                    "bandwidth_down", "bandwidth_up", "bandwidth_string",
                ],
            ),

            # 💰 Costs
            ObjectFieldsPanel(
                label="Cost Information",
                weight=150,
                section=SectionChoices.RIGHT_HALF,
                fields=[
                    "cost_in", "cost_out", "initial_cost", "express_cost",
                    "dekningsbidrag", "dekningsgrad",
                ],
            ),

            # 🕒 Dates
            ObjectFieldsPanel(
                label="Dates",
                weight=160,
                section=SectionChoices.RIGHT_HALF,
                fields=[
                    "order_date", "desired_delivery_date", "actually_delivery_date",
                    "order_delivery_date", "install_date", "live_date",
                    "start_invoice_date", "termination_date", "termination_order_date",
                ],
            ),

            # 🏢 Vendor
            ObjectFieldsPanel(
                label="Vendor",
                weight=170,
                section=SectionChoices.RIGHT_HALF,
                fields=[
                    "vendor", "vendor_id",
                ],
            ),

            # 🧾 References
            ObjectFieldsPanel(
                label="Reference Numbers",
                weight=180,
                section=SectionChoices.RIGHT_HALF,
                fields=[
                    "sambandsnummer", "smbnr_nhn", "smbnr_orig", "smbnr_prefix",
                ],
            ),

            # 🔗 Relationships & Extras
            ObjectFieldsPanel(
                label="Relationships & Metadata",
                weight=190,
                section=SectionChoices.RIGHT_HALF,
                fields=[
                    "transporttype", "transporttype_id", "connection_url",
                    "details_included", "parents",
                ],
            ),
        ],
        extra_buttons=[
            Button(
                weight=100,
                label="Map",
                icon="mdi-map-marker",
                link_name="plugins:praksis_nhn_nautobot:samband_map",
                color=ButtonColorChoices.BLUE
            ),
            Button(
                weight=125,
                label="Graph",
                icon="mdi-chart-histogram",
                link_name="plugins:praksis_nhn_nautobot:samband_graph_focus",
                color=ButtonColorChoices.BLUE
            ),
            DropdownButton(
                weight=150,
                label="dropdown",
                children=[
                    Button(
                        weight=100,
                        label="Map",
                        icon="mdi-map-marker",
                        link_name="plugins:praksis_nhn_nautobot:samband_map",
                        color=ButtonColorChoices.BLUE
                    ),
                    Button(
                        weight=150,
                        label="Graph",
                        icon="mdi-chart-histogram",
                        link_name="plugins:praksis_nhn_nautobot:samband_graph_focus",
                        color=ButtonColorChoices.BLUE
                    ),
                ]
            )
        ],
        # TODO implement drop-down button
    )
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET:
            # Generate a cache key from the current filters
            cache_key = f"samband_filtered_{urlencode(sorted(self.request.GET.items()))}"
            # Store the queryset IDs in cache (can't pickle querysets directly)
            object_ids = list(queryset.values_list('id', flat=True))
            cache.set(cache_key, object_ids, 300)  # Cache for 5 minutes

        return queryset


class SambandGraphFocusView(generic.ObjectView):
    """Graph visualization for Samband."""
    
    queryset = models.Samband.objects.all()
    template_name = "praksis_nhn_nautobot/focus_graph.html"
    
    def get_extra_context(self, request, instance):
        """Add graph data to the template context."""
        context = super().get_extra_context(request, instance)
        
        # Get requested depth from query parameters (default: 2)
        depth = int(request.GET.get('depth', 2))
        
        hierarchy_data = SambandGraphService.get_relations(instance, depth)
        serialized_data = SambandSerializer(hierarchy_data, many=True, context={'request': self.request}).data
        graph_data = SambandGraphService.create_network_graph(serialized_data)
        
        # Visualization options for focal view (hierarchical layout)
        options = {
            "nodes": {
                "shape": "dot",
                "size": 20,
                "font": {
                    "size": 14,
                    "face": "Tahoma",
                    "multi": True,
                    "align": "center",
                },
                "labelHighlightBold": False,
            },
            "edges": {
                "arrows": {
                    "to": {"enabled": True, "scaleFactor": 0.5}
                },
                "color": {"inherit": False},
                "smooth": {"enabled": True, "type": "dynamic"},
                "hoverWidth": 0
            },
            "physics": {
                "enabled": False,
            },
            "interaction": {
                "hover": True,
                "multiselect": False,
                "dragNodes": False
            },
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "direction": "UD",  # Up-Down layout
                    "sortMethod": "directed",
                    "nodeSpacing": 260,
                    "levelSeparation": 190
                }
            }
        }
        
        # Add graph data to context
        context['network_data'] = graph_data
        context['network_options'] = options
        context['depth'] = depth
        
        return context


class SambandGraphView(generic.View):
    template_name = "praksis_nhn_nautobot/network_graph.html"

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
    
    def get_queryset(self):        
        if self.request.GET:
            # Try to get cached results with the same key used in list view
            cache_key = f"samband_filtered_{urlencode(sorted(self.request.GET.items()))}"
            cached_ids = cache.get(cache_key)
            
            if cached_ids:
                # Use the cached object IDs
                return Samband.objects.filter(id__in=cached_ids)
        
        # If no cache or cache miss, fall back to filtering again
        queryset = Samband.objects.all()        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = {} 
        queryset = self.get_queryset()

        serialized_data = SambandSerializer(queryset, many=True, context={'request': self.request}).data
        graph_data = SambandGraphService.create_network_graph(serialized_data)
        
        # Visualization options
        options = {
            "nodes": {
                "shape": "dot",
                "size": 20,
                "font": {
                    "size": 14,
                    "face": "Tahoma",
                    "multi": True,
                    "align": "center",
                },
                "labelHighlightBold": False,
            },
            "edges": {
                "arrows": {
                    "to": {"enabled": True, "scaleFactor": 0.5}
                },
                "color": {"inherit": False},
                "smooth": {"enabled": True, "type": "dynamic"},
                "hoverWidth": 0
            },
            "physics": {
                "enabled": False,
            },
            "interaction": {
                "hover": True,
                "multiselect": False,
                "dragNodes": False
            }
        }
        
        # Add to context (convert Python objects to JSON strings for the template)
        context['network_data'] = graph_data
        context['network_options'] = options
        
        return context


class SambandMultipleMapView(TemplateView):
    """View for displaying a map of multiple connections."""
    template_name = "praksis_nhn_nautobot/samband_map_clientside.html"
    
    def get_filter_options(self):
        # Get unique filter values
        vendors = Samband.objects.values_list('vendor', flat=True).distinct().order_by('vendor')
        statuses = Samband.objects.values_list('status', flat=True).distinct().order_by('status')
        citylist = Samband.objects.values_list('location', flat=True).distinct().order_by('location')
        location_types = Samband.objects.values_list('location_type', flat=True).distinct().order_by('location_type')
        transport_types = Samband.objects.values_list('transporttype', flat=True).distinct().order_by('transporttype')

        # Filter out None/empty values
        vendors = [v for v in vendors if v]
        statuses = [s for s in statuses if s]
        citylist = [c for c in citylist if c]
        location_types = [lt for lt in location_types if lt]
        transport_types = [tt for tt in transport_types if tt]
        
        return {
            'vendors': vendors,
            'statuses': statuses,
            'citylist': citylist,
            'location_types': location_types,
            'transport_types': transport_types
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters from request
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')
        radius = self.request.GET.get('radius')
        
        # Handle multiple selections
        vendors = self.request.GET.getlist('vendor')
        statuses = self.request.GET.getlist('status')
        citylist = self.request.GET.getlist('location')
        location_types = self.request.GET.getlist('location_type')
        transport_types = self.request.GET.getlist('transporttype')
        
        # Get filter options
        filter_options = self.get_filter_options()
        context.update(filter_options)
        
        # Add selected values to context
        if vendors:
            context['selected_vendors'] = vendors
        if statuses:
            context['selected_statuses'] = statuses
        if citylist:
            context['selected_citylist'] = citylist
        if location_types:
            context['selected_location_types'] = location_types
        if transport_types:
            context['selected_transport_types'] = transport_types
        
        # Add location parameters to context
        if lat:
            context['lat'] = lat
        if lng:
            context['lng'] = lng
        if radius:
            context['radius'] = radius
        else:
            context['radius'] = '100'
        
        context['title'] = 'Network Connections Map'
        
        return context

class SambandMapView(TemplateView):
    """View for displaying a map of a single connection."""
    template_name = "praksis_nhn_nautobot/single_samband_view.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the connection ID from the URL
        pk = self.kwargs.get('pk')
        
        # Add connection ID to the context - this is all you need for JavaScript to fetch data
        context['connection_id'] = pk
        
        # Add a generic title (this will be updated via JavaScript)
        context['title'] = "Connection Map"
        
        return context
