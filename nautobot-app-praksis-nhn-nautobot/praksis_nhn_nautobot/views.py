"""Views for praksis_nhn_nautobot."""

from django.urls import reverse
from nautobot.apps.views import NautobotUIViewSet

from nautobot.core.views import generic

from praksis_nhn_nautobot import filters, forms, models, tables
from praksis_nhn_nautobot.api import serializers

from django.http import HttpResponse

def custom_home(request):
    """Super simple home view for testing."""
    return HttpResponse("<h1>Custom NHN Homepage</h1><p>URL override is working!</p>")


class NHNModelUIViewSet(NautobotUIViewSet):
    """ViewSet for NHNModel views."""

    bulk_update_form_class = forms.NHNModelBulkEditForm
    filterset_class = filters.NHNModelFilterSet
    filterset_form_class = forms.NHNModelFilterForm
    form_class = forms.NHNModelForm
    lookup_field = "pk"
    queryset = models.NHNModel.objects.all()
    serializer_class = serializers.NHNModelSerializer
    table_class = tables.NHNModelTable

    # action_buttons = ("add", "bulk_edit", "bulk_delete")

    # # In your NHNModelUIViewSet class:
    # def get_extra_context(self, request, instance):
    #     context = super().get_extra_context(request, instance)
        
    #     # Add graph button to the detail view
    #     if instance and request.path.endswith(f"{instance.pk}/"):
    #         context["extra_buttons"] = [
    #             {
    #                 "title": "Hierarchy Graph",
    #                 "icon_class": "mdi mdi-graph",
    #                 "url": reverse("plugins:praksis_nhn_nautobot:nhnmodel_graph", kwargs={"pk": instance.pk}),
    #                 "permissions": ["praksis_nhn_nautobot.view_nhnmodel"],
    #             }
    #         ]
        
    #     return context

# Add this to your existing views.py file
class NHNModelGraphView(generic.ObjectView):
    """Graph visualization for NHNModel."""
    
    queryset = models.NHNModel.objects.all()
    template_name = "praksis_nhn_nautobot/graph_view.html"


from django.shortcuts import render

def nhn_dashboard(request):
    """NHN Dashboard view - a custom homepage for NHN functionality."""
    
    # Get recent connections
    try:
        # Get the most recently updated connections, limited to 5
        recent_connections = models.NHNModel.objects.all().order_by('-last_updated')[:5]
    except Exception as e:
        print(f"Error fetching recent connections: {e}")
        recent_connections = []
    
    
    # Prepare context for the template
    context = {
        'recent_connections': recent_connections,
    }
    
    return render(request, 'praksis_nhn_nautobot/dashboard.html', context)
