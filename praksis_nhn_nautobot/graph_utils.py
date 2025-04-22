# filepath: praksis_nhn_nautobot/graph_utils.py
import networkx as nx
from pyvis.network import Network
from .models import Samband  # Assuming Samband model is in models.py

def get_related_sambands(samband, depth=1, relation_type='all', processed=None):
    """
    Recursively fetches related Samband objects (parents or children or both).
    Similar logic to _get_relation_tree in views.py but returns actual objects.
    """
    if processed is None:
        processed = set()

    if depth <= 0 or samband.id in processed:
        return [], processed

    processed.add(samband.id)
    related_nodes = []

    # Fetch parents
    if relation_type in ['all', 'parents']:
        parents = samband.parents.all()
        for parent in parents:
            if parent.id not in processed:
                related_nodes.append({'samband': parent, 'type': 'parent', 'depth': 1})
                sub_related, processed = get_related_sambands(parent, depth - 1, relation_type, processed)
                related_nodes.extend(sub_related) # Adjust depth info if needed

    # Fetch children
    if relation_type in ['all', 'children']:
        children = samband.children.all()
        for child in children:
             if child.id not in processed:
                related_nodes.append({'samband': child, 'type': 'child', 'depth': 1})
                sub_related, processed = get_related_sambands(child, depth - 1, relation_type, processed)
                related_nodes.extend(sub_related) # Adjust depth info if needed

    # Basic deduplication based on ID, keeping the first encountered type/depth
    final_nodes = []
    seen_ids = set()
    for node_info in related_nodes:
        if node_info['samband'].id not in seen_ids:
            final_nodes.append(node_info)
            seen_ids.add(node_info['samband'].id)

    return final_nodes, processed


def generate_focused_pyvis_html(samband_id, depth=1):
    """
    Generates PyVis HTML for a single focused Samband and its relatives.
    """
    try:
        center_samband = Samband.objects.get(pk=samband_id)
    except Samband.DoesNotExist:
        return "<p>Samband not found.</p>"

    # Fetch related nodes using the helper
    related_nodes_info, _ = get_related_sambands(center_samband, depth=depth)

    # Initialize PyVis Network
    net = Network(notebook=True, cdn_resources='remote', height='750px', width='100%', select_menu=True, filter_menu=True)
    net.set_options("""
    {
      "layout": {
        "hierarchical": {
          "enabled": true,
          "levelSeparation": 200,
          "nodeSpacing": 150,
          "treeSpacing": 250,
          "direction": "UD",
          "sortMethod": "directed"
        }
      },
      "physics": {
         "enabled": false,
         "hierarchicalRepulsion": {
            "nodeDistance": 150
         }
      },
      "nodes": {
        "font": {
          "size": 12
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.5
          }
        },
        "smooth": {
             "type": "cubicBezier",
             "forceDirection": "vertical",
             "roundness": 0.4
        }
      }
    }
    """)


    # Add center node
    net.add_node(
        str(center_samband.pk),
        label=f"{center_samband.name}\n({center_samband.sambandsnummer})",
        title=f"Name: {center_samband.name}\nID: {center_samband.pk}\nType: Current",
        color='#3498db', # Blue for current
        shape='ellipse',
        level=0 # Center level
    )

    # Add related nodes and edges
    all_nodes = {str(center_samband.pk)} # Keep track of added nodes
    for node_info in related_nodes_info:
        related_samband = node_info['samband']
        node_id = str(related_samband.pk)
        node_type = node_info['type']
        node_depth = node_info['depth'] # Relative depth from center

        if node_id not in all_nodes:
             # Determine color and level based on type
            if node_type == 'parent':
                color = '#2ecc71' # Green for parent
                level = -node_depth # Parents above
            elif node_type == 'child':
                color = '#e74c3c' # Red for child
                level = node_depth # Children below
            else:
                color = '#95a5a6' # Grey for others (if any)
                level = node_depth # Default level

            net.add_node(
                node_id,
                label=f"{related_samband.name}\n({related_samband.sambandsnummer})",
                title=f"Name: {related_samband.name}\nID: {related_samband.pk}\nType: {node_type.capitalize()}",
                color=color,
                shape='box',
                level=level
            )
            all_nodes.add(node_id)

        # Add edge (handle potential duplicates if relationships exist both ways)
        if node_type == 'parent':
             # Edge from parent to center
             if (node_id, str(center_samband.pk)) not in [(e['from'], e['to']) for e in net.edges]:
                net.add_edge(node_id, str(center_samband.pk))
        elif node_type == 'child':
             # Edge from center to child
             if (str(center_samband.pk), node_id) not in [(e['from'], e['to']) for e in net.edges]:
                net.add_edge(str(center_samband.pk), node_id)

    # Generate HTML
    # Consider saving to a temporary file or returning the HTML string directly
    html_content = net.generate_html(f'pyvis_focus_{samband_id}.html', local=False) # Use local=False for CDN
    # Or return net.html for direct embedding without file saving
    return net.html # Return raw HTML string


def generate_set_pyvis_html(samband_ids):
    """
    Generates PyVis HTML for a specific set of Samband IDs, showing connections between them.
    """
    if not samband_ids:
        return "<p>No Samband IDs provided.</p>"

    sambands = Samband.objects.filter(pk__in=samband_ids).prefetch_related('parents', 'children')
    if not sambands.exists():
         return "<p>None of the provided Samband IDs were found.</p>"

    # Initialize PyVis Network (non-hierarchical)
    net = Network(notebook=False, cdn_resources='in_line', height='600px', width='100%')
    
    net.set_options("""
    var options = {
      "physics": {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "stabilization": {
          "iterations": 150
        }
      },
      "nodes": {
        "font": {
          "size": 12
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.5
          }
        },
        "smooth": false
      }
    }
    """)

    

    valid_ids_set = {str(s.pk) for s in sambands}

    # Add nodes from the set
    for samband in sambands:
        net.add_node(
            str(samband.pk),
            label=f"{samband.name}\n({samband.sambandsnummer})",
            title=f"Name: {samband.name}\nID: {samband.pk}",
            shape='ellipse' # Or box, circle etc.
        )

    # Add edges *only* between nodes in the set
    for samband in sambands:
        current_id_str = str(samband.pk)
        # Check parents
        for parent in samband.parents.all():
            parent_id_str = str(parent.pk)
            if parent_id_str in valid_ids_set:
                # Add edge from parent to current node if not already added
                 if (parent_id_str, current_id_str) not in [(e['from'], e['to']) for e in net.edges]:
                    net.add_edge(parent_id_str, current_id_str)

        # Check children (avoid duplicating edges added via parent check)
        for child in samband.children.all():
            child_id_str = str(child.pk)
            if child_id_str in valid_ids_set:
                # Add edge from current node to child if not already added
                if (current_id_str, child_id_str) not in [(e['from'], e['to']) for e in net.edges]:
                    net.add_edge(current_id_str, child_id_str)

    # Generate HTML
    html_content = net.generate_html(f'pyvis_set_{"_".join(map(str, samband_ids[:5]))}.html', local=False)
    return net.html # Return raw HTML string
