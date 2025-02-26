"""API views for praksis_nhn_nautobot.
Viewset innenfor Rest Framework: list, retrieve, create, update og delete funksjonalitet
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from nautobot.apps.api import NautobotModelViewSet

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.api import serializers


class NHNModelViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """NHNModel viewset."""

    queryset = models.NHNModel.objects.all()
    serializer_class = serializers.NHNModelSerializer
    filterset_class = filters.NHNModelFilterSet

    @action(detail=True, methods=['get'])
    def parents(self, request, pk=None):
        """Return all parent connections."""
        obj = self.get_object()
        parents = obj.parents.all()
        serializer = serializers.ParentNHNModelSerializer(parents, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Return all child connections."""
        obj = self.get_object()
        children = obj.children.all()
        serializer = serializers.ParentNHNModelSerializer(children, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """Return complete hierarchy (parent tree and child tree)."""
        obj = self.get_object()
        
        # Get all parents recursively (up to 3 levels)
        parent_tree = self._get_parent_tree(obj, max_depth=3)
        
        # Get all children recursively (up to 3 levels)
        child_tree = self._get_child_tree(obj, max_depth=3)
        
        return Response({
            'parent_tree': parent_tree,
            'child_tree': child_tree,
        })
    
    def _get_parent_tree(self, obj, current_depth=0, max_depth=3, processed=None):
        """Recursively build parent tree."""
        if processed is None:
            processed = set()
            
        if current_depth >= max_depth or obj.id in processed:
            return None
            
        processed.add(obj.id)
        
        parents_data = []
        for parent in obj.parents.all():
            parent_data = {
                'id': parent.id,
                'name': str(parent),
                'sambandsnummer': parent.sambandsnummer,
                'parents': self._get_parent_tree(
                    parent, current_depth + 1, max_depth, processed
                )
            }
            parents_data.append(parent_data)
            
        return parents_data if parents_data else None
    
    def _get_child_tree(self, obj, current_depth=0, max_depth=3, processed=None):
        """Recursively build child tree."""
        if processed is None:
            processed = set()
            
        if current_depth >= max_depth or obj.id in processed:
            return None
            
        processed.add(obj.id)
        
        children_data = []
        for child in obj.children.all():
            child_data = {
                'id': child.id,
                'name': str(child),
                'sambandsnummer': child.sambandsnummer,
                'children': self._get_child_tree(
                    child, current_depth + 1, max_depth, processed
                )
            }
            children_data.append(child_data)
            
        return children_data if children_data else None

    @action(detail=True, methods=['post'])
    def add_parent(self, request, pk=None):
        """Add a parent to this connection."""
        obj = self.get_object()
        parent_id = request.data.get('parent_id')
        
        try:
            parent = models.NHNModel.objects.get(pk=parent_id)
        except models.NHNModel.DoesNotExist:
            return Response({'detail': f'Parent with ID {parent_id} not found.'}, status=404)
            
        # Check for circular reference
        if obj == parent:
            return Response({'detail': 'Cannot add connection as its own parent.'}, status=400)
            
        obj.parents.add(parent)
        return Response({'detail': f'Added {parent} as parent of {obj}'})

    @action(detail=True, methods=['post'])
    def remove_parent(self, request, pk=None):
        """Remove a parent from this connection."""
        obj = self.get_object()
        parent_id = request.data.get('parent_id')
        
        try:
            parent = models.NHNModel.objects.get(pk=parent_id)
        except models.NHNModel.DoesNotExist:
            return Response({'detail': f'Parent with ID {parent_id} not found.'}, status=404)
            
        if parent not in obj.parents.all():
            return Response({'detail': f'{parent} is not a parent of {obj}'}, status=400)
            
        obj.parents.remove(parent)
        return Response({'detail': f'Removed {parent} as parent of {obj}'})