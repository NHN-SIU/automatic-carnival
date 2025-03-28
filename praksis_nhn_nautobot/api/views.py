"""API views for praksis_nhn_nautobot."""

from rest_framework.decorators import action
from rest_framework.response import Response
from nautobot.apps.api import NautobotModelViewSet

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.api import serializers

from praksis_nhn_nautobot.models import Samband
from praksis_nhn_nautobot.services.graph_service import SambandGraphService
from django.http import JsonResponse

class SambandViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """Samband viewset."""

    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    filterset_class = filters.SambandFilterSet
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """Return hierarchy of tree (parents and children)"""
        try:
            samband = self.get_object()
        except Samband.DoesNotExist:
            return JsonResponse({'error': 'Samband not found'}, status=404)
        
        # Get parameters from request
        depth = int(request.GET.get('depth', 1))
        
        # Use the service to generate graph data
        graph_data = SambandGraphService.generate_graph_data(samband, depth)
        
        # Return the graph data with samband details
        return JsonResponse({
            'graph_data': graph_data,
            'samband': {
                'id': str(samband.pk),
                'name': str(samband),
                'sambandsnummer': samband.sambandsnummer
            }
        })