"""Service for processing Samband graph data."""

class SambandGraphService:
    """Service to handle Samband graph data generation."""
    
    @staticmethod
    def get_relation_tree(obj, relation_type='parents', current_depth=0, max_depth=3, processed=None):
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
                next_relation_key: SambandGraphService.get_relation_tree(
                    relation, relation_type, current_depth + 1, max_depth, processed.copy()
                )
            }
            relations_data.append(relation_data)
            
        return relations_data if relations_data else None
    
    @staticmethod
    def flatten_tree(tree):
        """Convert a nested tree to a flat list of direct relationships."""
        if not tree:
            return []
        
        # Return only top-level relations (no nesting)
        return [{k: v for k, v in item.items() if k != 'parents' and k != 'children'} 
                for item in tree]
    
    @staticmethod
    def prepare_graph_data(current_node, parent_tree, child_tree):
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
            SambandGraphService.process_relation_tree(parent_tree, nodes, links, current_id, True)
        
        # Process child tree
        if child_tree:
            SambandGraphService.process_relation_tree(child_tree, nodes, links, current_id, False)
        
        return {
            'nodes': nodes,
            'links': links
        }
    
    @staticmethod
    def process_relation_tree(tree, nodes, links, connected_id, is_parent, current_depth=0):
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
                SambandGraphService.process_relation_tree(
                    relation[next_relations_key], 
                    nodes, 
                    links, 
                    relation_id, 
                    is_parent, 
                    current_depth + 1
                )
    
    @classmethod
    def generate_graph_data(cls, instance, depth=2):
        """Generate complete graph data for a Samband instance."""
        parent_tree = cls.get_relation_tree(instance, 'parents', max_depth=depth)
        child_tree = cls.get_relation_tree(instance, 'children', max_depth=depth)

        return cls.prepare_graph_data(instance, parent_tree, child_tree)

    @classmethod
    def generate_filtered_graph_data(cls, queryset):
        """
        Generate graph data for a filtered set of Samband objects.
        
        Args:
            queryset: QuerySet of Samband objects to include in the graph
            
        Returns:
            dict: Contains 'nodes' and 'links' arrays for D3 visualization
        """
        nodes = []
        links = []
        processed_ids = set()
         
        # Create a set of all IDs in the queryset for faster lookups
        queryset_ids = set(str(obj.id) for obj in queryset)
        
        # First pass: Create all nodes
        for obj in queryset:
            obj_id = str(obj.id)
            
            # Skip if we've already processed this node
            if obj_id in processed_ids:
                continue
                
            # Add node
            nodes.append({
                'id': obj_id,
                'name': str(obj),
                'sambandsnummer': obj.sambandsnummer,
                'type': 'filtered'  # Mark as part of filtered set
            })
            
            processed_ids.add(obj_id)
        
        # Second pass: Add links between nodes, but only if both ends are in our queryset
        for obj in queryset:
            obj_id = str(obj.id)
            
            # Add links to parents (if parents are in the filtered set)
            for parent in obj.parents.all():
                parent_id = str(parent.id)
                if parent_id in queryset_ids:
                    links.append({
                        'source': parent_id,
                        'target': obj_id,
                        'type': 'parent-child'
                    })
            
            # Add links to children (if children are in the filtered set)
            for child in obj.children.all():
                child_id = str(child.id)
                if child_id in queryset_ids:
                    links.append({
                        'source': obj_id,
                        'target': child_id,
                        'type': 'parent-child'
                    })
        
        return {
            'nodes': nodes,
            'links': links
        }