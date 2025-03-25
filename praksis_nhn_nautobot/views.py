"""Views for praksis_nhn_nautobot."""

from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.views import generic

from praksis_nhn_nautobot import filters, forms, models, tables
from praksis_nhn_nautobot.api import serializers


class SambandUIViewSet(NautobotUIViewSet):
    """ViewSet for Samband views."""

    bulk_update_form_class = forms.SambandBulkEditForm
    filterset_class = filters.SambandFilterSet
    filterset_form_class = forms.SambandFilterForm
    form_class = forms.SambandForm
    lookup_field = "pk"
    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    table_class = tables.SambandTable

class SambandGraphView(generic.ObjectView):
    """Graph visualization for Samband."""
    
    queryset = models.Samband.objects.all()
    template_name = "praksis_nhn_nautobot/graph_view.html"
    
    def get_extra_context(self, request, instance):
        """Add graph data to the template context."""
        context = super().get_extra_context(request, instance)
        
        # Get requested depth from query parameters (default: 2)
        depth = int(request.GET.get('depth', 2))
        
        # Get view mode from query parameters (default: hierarchy)
        mode = request.GET.get('mode', 'hierarchy')
        
        # Build the complete hierarchy data
        parent_tree = self._get_relation_tree(instance, 'parents', max_depth=depth)
        child_tree = self._get_relation_tree(instance, 'children', max_depth=depth)
        
        # Prepare the graph data based on mode
        if mode == 'parents':
            # Only direct parent relationships
            graph_data = self._prepare_graph_data(
                instance, 
                self._flatten_tree(parent_tree), 
                []
            )
        elif mode == 'children':
            # Only direct child relationships
            graph_data = self._prepare_graph_data(
                instance, 
                [], 
                self._flatten_tree(child_tree)
            )
        else:
            # Complete hierarchy
            graph_data = self._prepare_graph_data(instance, parent_tree, child_tree)
        
        # Add data and options to context
        context.update({
            'graph_data': graph_data,
            'current_depth': depth,
            'current_mode': mode,
            'depth_options': [1, 2, 3],
            'samband_json': {
                'id': str(instance.pk),
                'name': str(instance),
                'sambandsnummer': instance.sambandsnummer
            }
        })
        return context
    
    def _get_relation_tree(self, obj, relation_type='parents', current_depth=0, max_depth=3, processed=None):
        """
        Recursively build relation tree (parents or children).
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
                'id': str(relation.id),
                'name': str(relation),
                'sambandsnummer': relation.sambandsnummer,
                'depth': current_depth,
                next_relation_key: self._get_relation_tree(
                    relation, relation_type, current_depth + 1, max_depth, processed
                )
            }
            relations_data.append(relation_data)
            
        return relations_data if relations_data else None
    
    def _flatten_tree(self, tree):
        """Convert a nested tree to a flat list of direct relationships."""
        if not tree:
            return []
        
        # Return only top-level relations (no nesting)
        return [{k: v for k, v in item.items() if k != 'parents' and k != 'children'} 
                for item in tree]
    
    def _prepare_graph_data(self, current_node, parent_tree, child_tree):
        """
        Prepare graph data structure for D3 visualization.
        
        Returns:
            dict: Contains 'nodes' and 'links' arrays for D3
        """
        nodes = []
        links = []
        
        # Add current node
        current_id = str(current_node.id)
        nodes.append({
            'id': current_id,
            'name': str(current_node),
            'sambandsnummer': current_node.sambandsnummer,
            'type': 'current'
        })
        
        # Process parent tree
        if parent_tree:
            self._process_relation_tree(parent_tree, nodes, links, current_id, True)
        
        # Process child tree
        if child_tree:
            self._process_relation_tree(child_tree, nodes, links, current_id, False)
        
        return {
            'nodes': nodes,
            'links': links
        }
    
    def _process_relation_tree(self, tree, nodes, links, connected_id, is_parent, current_depth=0):
        """
        Process a relation tree and add nodes and links.
        
        Args:
            tree: List of relation objects (can be nested)
            nodes: List to add nodes to
            links: List to add links to
            connected_id: ID of the node these relations connect to
            is_parent: True if these are parent relations, False for children
            current_depth: Current recursion depth
        """
        if not tree:
            return
        
        for relation in tree:
            # Skip if relation has no ID
            if 'id' not in relation:
                continue
                
            relation_id = relation['id']
            
            # Add node if it doesn't exist
            if not any(n['id'] == relation_id for n in nodes):
                nodes.append({
                    'id': relation_id,
                    'name': relation.get('name', 'Unknown'),
                    'sambandsnummer': relation.get('sambandsnummer', ''),
                    'depth': relation.get('depth', current_depth),
                    'type': 'parent' if is_parent else 'child'
                })
            
            # Add link
            links.append({
                'source': relation_id if is_parent else connected_id,
                'target': connected_id if is_parent else relation_id,
                'type': 'parent-child'
            })
            
            # Process nested relations if they exist
            next_relations_key = 'parents' if is_parent else 'children'
            if next_relations_key in relation and relation[next_relations_key]:
                self._process_relation_tree(
                    relation[next_relations_key], 
                    nodes, 
                    links, 
                    relation_id, 
                    is_parent, 
                    current_depth + 1
                )