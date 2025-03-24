"""API views for praksis_nhn_nautobot."""

from rest_framework.decorators import action
from rest_framework.response import Response
from nautobot.apps.api import NautobotModelViewSet

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.api import serializers


class SambandViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """Samband viewset."""

    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    filterset_class = filters.SambandFilterSet
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """Return complete hierarchy (parent tree and child tree)."""
        obj = self.get_object()
        
        # Get all parents recursively (up to 3 levels)
        parent_tree = self._get_relation_tree(obj, relation_type='parents', max_depth=3)
        
        # Get all children recursively (up to 3 levels)
        child_tree = self._get_relation_tree(obj, relation_type='children', max_depth=3)
        
        return Response({
            'parent_tree': parent_tree,
            'child_tree': child_tree,
        })

    def _get_relation_tree(self, obj, relation_type='parents', current_depth=0, max_depth=3, processed=None):
        """
        Recursively build relation tree (parents or children).
        
        Args:
            obj: The Samband object to get relations for
            relation_type: Either 'parents' or 'children'
            current_depth: Current recursion depth
            max_depth: Maximum recursion depth
            processed: Set of already processed object IDs
        
        Returns:
            List of relation objects with their own relations, or None
        """
        if processed is None:
            processed = set()
            
        if current_depth >= max_depth or obj.id in processed:
            return None
            
        processed.add(obj.id)
        
        relations_data = []
        
        # Get the correct relation based on type
        if relation_type == 'parents':
            relations = obj.parents.all()
            next_relation_key = 'parents'
        else:  # relation_type == 'children'
            relations = obj.children.all()
            next_relation_key = 'children'
        
        for relation in relations:
            relation_data = {
                'id': relation.id,
                'name': str(relation),
                'sambandsnummer': relation.sambandsnummer,
                'depth': current_depth,
                next_relation_key: self._get_relation_tree(
                    relation, relation_type, current_depth + 1, max_depth, processed
                )
            }
            relations_data.append(relation_data)
            
        return relations_data if relations_data else None