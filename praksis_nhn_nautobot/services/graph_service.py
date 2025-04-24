"""Module for handling graph data and HTML generation for Samband instances."""

from collections import deque

from praksis_nhn_nautobot.models import Samband


class SambandGraphService:
    """Service to handle Samband graph data and html generation."""

    @staticmethod
    def create_network_graph(sambands_data):
        """
        Creates a network graph from Samband data using NetworkX.

        Args:
            sambands_data (list): List of Samband instances in JSON format

        Returns:
            dict: JSON data with nodes and links for graph visualization
        """
        import networkx as nx

        # Create a directed graph
        G = nx.DiGraph()

        # Create mapping of id to samband data for quick lookup
        samband_map = {samband["id"]: samband for samband in sambands_data}

        # Add nodes with attributes
        for samband in sambands_data:
            G.add_node(
                samband["id"],
                id=samband["id"],
                name=samband["name"],
                type=samband["type"],
                status=samband["status"],
                sambandsnummer=samband["sambandsnummer"],
                bandwidth=samband["bandwidth_string"],
                vendor=samband["vendor"],
                location=samband["location"],
                transporttype=samband["transporttype"],
            )

        # Add edges based on parent relationships
        for samband in sambands_data:
            for parent in samband.get("parents", []):
                # Get parent ID as string
                parent_id = str(parent["id"])
                if parent_id in samband_map:  # Only add edge if parent exists in our data
                    G.add_edge(parent_id, samband["id"])

        # # Convert NetworkX graph to Vis.js format
        nodes = []
        for node_id, node_attrs in G.nodes(data=True):
            # Create the node object with ID and all attributes
            node = {
                "id": node_id,
                "label": node_attrs.get("name", f"Node {node_id}"),
                "name": node_attrs.get("name", ""),
                "type": node_attrs.get("type", ""),
                "status": node_attrs.get("status", ""),
                "sambandsnummer": node_attrs.get("sambandsnummer", ""),
                "bandwidth": node_attrs.get("bandwidth", ""),
                "vendor": node_attrs.get("vendor", ""),
                "location": node_attrs.get("location", ""),
                "transporttype": node_attrs.get("transporttype", ""),
            }
            nodes.append(node)

        # Extract edges
        edges = []
        for source, target in G.edges():
            edge = {"from": source, "to": target, "arrows": "to"}
            edges.append(edge)

        return {"nodes": nodes, "edges": edges}

    @classmethod
    def get_relations(cls, instance, depth=2):
        parents = cls._traverse_graph(instance, depth, direction="up")
        children = cls._traverse_graph(instance, depth, direction="down")
        return [instance] + parents + children

    @staticmethod
    def _traverse_graph(instance, depth, direction="up"):
        """
        Generic method to traverse the graph in either direction using BFS.
        
        Args:
            instance: The Samband object to start traversal from
            depth: How many levels to traverse
            direction: "up" for parents, "down" for children
            
        Returns:
            list: List of related objects
        """
        result = []
        visited = set()  # To track visited nodes
        
        # Initialize queue based on direction
        if direction == "up":
            queue = deque([(parent, 1) for parent in instance.parents.all()])
        else:  # direction == "down"
            queue = deque([(child, 1) for child in Samband.objects.filter(parents=instance)])
        
        while queue:
            current_node, current_depth = queue.popleft()

            # Skip if we've already processed this node or exceeded depth
            if current_node.id in visited or current_depth > depth:
                continue

            visited.add(current_node.id)
            result.append(current_node)
            
            # If we haven't reached max depth, add next level nodes to the queue
            if current_depth < depth:
                if direction == "up":
                    next_nodes = current_node.parents.all()
                else:  # direction == "down"
                    next_nodes = Samband.objects.filter(parents=current_node)
                    
                for next_node in next_nodes:
                    queue.append((next_node, current_depth + 1))
        
        return result
