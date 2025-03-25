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

"""Views for praksis_nhn_nautobot."""

import json
import os
import tempfile
from collections import deque

import networkx as nx
from django.conf import settings
from django.utils.safestring import mark_safe
from nautobot.apps.views import NautobotUIViewSet
from nautobot.core.views import generic
from pyvis.network import Network

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
    """Graph visualization for Samband using NetworkX and PyVis."""
    
    queryset = models.Samband.objects.all()
    template_name = "praksis_nhn_nautobot/graph_view.html"
    
    def get_extra_context(self, request, instance):
        """Add graph data to the template context."""
        context = super().get_extra_context(request, instance)
        
        # Get requested depth from query parameters (default: 2)
        depth = int(request.GET.get('depth', 2))
        mode = request.GET.get('mode', 'hierarchy')
        
        # Create the network
        nodes, edges, _, _, _, options = self._create_network_graph(instance, depth, mode)

        # Add data and options to context
        context.update({
            'nodes_json': nodes,
            'edges_json': edges,
            'options_json': options,
            'current_depth': depth,
            'current_mode': mode,
            'depth_options': [1, 2, 3, 4],
        })
        return context
    
    def _create_network_graph(self, instance, depth, mode):
        """Create an interactive network graph using NetworkX and PyVis."""
        # Get nodes and links data
        nodes, links = self._get_graph_data_bfs(instance, depth, mode)
        
        # Create a directed graph with NetworkX
        G = nx.DiGraph()
        
        # Define node attributes based on type
        for node in nodes:
            node_id = node['id']
            node_type = node['type']
            
            # Set node color based on type
            if node_type == 'current':
                color = '#3498db'  # Blue for current node
                size = 25
                font = {'size': 18, 'face': 'Arial', 'color': 'black'}
                shape = 'dot'
            elif node_type == 'parent':
                color = '#2ecc71'  # Green for parent nodes
                size = 20
                font = {'size': 14, 'face': 'Arial', 'color': 'black'}
                shape = 'dot'
            else:  # child
                color = '#e74c3c'  # Red for child nodes
                size = 20
                font = {'size': 14, 'face': 'Arial', 'color': 'black'}
                shape = 'dot'
            
            # Create node tooltip with relevant information
            tooltip = f"{node['name']}"
            if node.get('sambandsnummer'):
                tooltip += f" (Sambandsnummer: {node['sambandsnummer']})"
            
            # Add node with attributes
            G.add_node(
                node_id,
                label=node['name'],
                title=tooltip,
                color=color,
                size=size,
                font=font,
                shape=shape
            )
        
        # Add edges with custom styling
        for link in links:
            G.add_edge(
                link['source'],
                link['target'],
                color='#95a5a6',  # Gray for edges
                width=1.5,
                arrows='to',  # Directed arrow
                arrowStrikethrough=False
            )
        
        # Create PyVis network
        net = Network(
            height="600px", 
            width="100%", 
            directed=True,
            bgcolor="#ffffff",
            font_color="black"
        )
        
        # Import from NetworkX
        net.from_nx(G)
        
        # Configure physics for better layout
        physics_options = {
            "enabled": True,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "maxVelocity": 50,
            "stabilization": {
                "enabled": True,
                "iterations": 1000,
                "updateInterval": 100
            }
        }
        
        # Different layout options based on mode
        if mode == 'hierarchy':
            layout_options = {
                "hierarchical": {
                    "enabled": True,
                    "levelSeparation": 150,
                    "direction": "UD",  # Up-Down layout
                    "sortMethod": "directed"
                }
            }
        elif mode == 'parents':
            layout_options = {
                "hierarchical": {
                    "enabled": True,
                    "levelSeparation": 150,
                    "direction": "DU",  # Down-Up layout (parents on top)
                    "sortMethod": "directed"
                }
            }
        else:  # mode == 'children'
            layout_options = {
                "hierarchical": {
                    "enabled": True,
                    "levelSeparation": 150,
                    "direction": "UD",  # Up-Down layout (children below)
                    "sortMethod": "directed"
                }
            }
        
        # Set options for better visualization
        net.set_options(json.dumps({
            "physics": physics_options,
            "layout": layout_options,
            "interaction": {
                "navigationButtons": True,
                "keyboard": True,
                "hover": True,
                "multiselect": False,
                "tooltipDelay": 300
            },
            "edges": {
                "smooth": {
                    "type": "cubicBezier",
                    "roundness": 0.5
                }
            }
        }))

        return net.get_network_data()
    
    def _get_graph_data_bfs(self, instance, max_depth=2, mode='hierarchy'):
        """
        Get graph data using Breadth-First Search for efficiency.
        
        Args:
            instance: The Samband instance to build the graph for
            max_depth: Maximum depth to traverse
            mode: 'hierarchy', 'parents', or 'children'
            
        Returns:
            Tuple of (nodes, links) where each is a list of dictionaries
        """
        nodes = []
        links = []
        visited = set()  # Track visited nodes to avoid cycles
        
        # Add the current node
        current_id = str(instance.id)
        nodes.append({
            'id': current_id,
            'name': str(instance),
            'sambandsnummer': instance.sambandsnummer,
            'type': 'current'
        })
        visited.add(current_id)
        
        # Determine which relation types to process based on mode
        process_parents = mode in ['hierarchy', 'parents']
        process_children = mode in ['hierarchy', 'children']
        
        # Process parent relationships if needed
        if process_parents:
            # Use a queue for BFS traversal
            queue = deque([(instance, 0)])  # (node, depth)
            
            while queue:
                node, depth = queue.popleft()
                
                # Skip if we've reached max depth
                if depth >= max_depth:
                    continue
                
                # Get all parents in one query
                for parent in node.parents.all():
                    parent_id = str(parent.id)
                    
                    # Add link
                    links.append({
                        'source': parent_id,
                        'target': str(node.id),
                        'type': 'parent-child'
                    })
                    
                    # Add node if not already visited
                    if parent_id not in visited:
                        nodes.append({
                            'id': parent_id,
                            'name': str(parent),
                            'sambandsnummer': parent.sambandsnummer,
                            'depth': depth + 1,
                            'type': 'parent'
                        })
                        visited.add(parent_id)
                        
                        # Queue for next level if not at max depth
                        if depth + 1 < max_depth:
                            queue.append((parent, depth + 1))
        
        # Process child relationships if needed
        if process_children:
            # Reset visited for children traversal (if only processing children)
            if not process_parents:
                visited = {current_id}
                
            # Use a separate queue for children
            queue = deque([(instance, 0)])  # (node, depth)
            
            while queue:
                node, depth = queue.popleft()
                
                # Skip if we've reached max depth
                if depth >= max_depth:
                    continue
                
                # Get all children in one query
                for child in node.children.all():
                    child_id = str(child.id)
                    
                    # Add link
                    links.append({
                        'source': str(node.id),
                        'target': child_id,
                        'type': 'parent-child'
                    })
                    
                    # Add node if not already visited
                    if child_id not in visited:
                        nodes.append({
                            'id': child_id,
                            'name': str(child),
                            'sambandsnummer': child.sambandsnummer,
                            'depth': depth + 1,
                            'type': 'child'
                        })
                        visited.add(child_id)
                        
                        # Queue for next level if not at max depth
                        if depth + 1 < max_depth:
                            queue.append((child, depth + 1))
        
        return nodes, links