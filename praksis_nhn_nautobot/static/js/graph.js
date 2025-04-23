/**
 * Network Graph Renderer
 * Handles visualization of network graphs using vis.js
 */
const NetworkGraphRenderer = {
  /**
   * Initialize the network graph
   * @param {string} containerId - ID of the container element
   */
  initialize: function (containerId) {
    const container = document.getElementById(containerId);

    // Get data from json_script tags
    const nodesData = JSON.parse(
      document.getElementById("nodes-data").textContent
    );
    const edgesData = JSON.parse(
      document.getElementById("edges-data").textContent
    );
    const fullNodesData = JSON.parse(
      document.getElementById("full-nodes-data").textContent
    );
    const options = JSON.parse(
      document.getElementById("options-data").textContent
    );

    // Check if we're in focus view
    let focusNodeId = null;
    const focusViewElement =
      document.getElementById("is-focus-view").textContent;

    if (focusViewElement == "true") {
      focusNodeId = nodesData[0].id;

      // Highlight the first node with a distinctive color
      nodesData[0].color = {
        background: "#FF9800", // Orange background
        border: "#E65100", // Dark orange border
        highlight: {
          background: "#FFB74D", // Lighter orange when highlighted
          border: "#E65100",
        },
      };
    }

    // Create a map for quick lookup of node data by ID
    const nodeDataMap = this.createNodeDataMap(fullNodesData);

    // Initialize vis.js network
    const { network, nodes, edges } = this.createNetwork(
      container,
      nodesData,
      edgesData,
      options
    );

    // Set up event handlers
    this.setupLabelHandlers(nodes, nodeDataMap);
    this.setupHoverEffects(network, nodes, edges, focusNodeId);
    this.setupClickHandler(network);

    return { network, nodes, edges, nodeDataMap };
  },

  /**
   * Create node data map for quick lookups
   * @param {Array} fullNodesData - Array of complete node data objects
   * @returns {Object} - Map of node IDs to node data
   */
  createNodeDataMap: function (fullNodesData) {
    const nodeDataMap = {};
    fullNodesData.forEach((node) => {
      nodeDataMap[node.id] = node;
    });
    return nodeDataMap;
  },

  /**
   * Create the vis.js network
   * @param {HTMLElement} container - Container element
   * @param {Array} nodesData - Array of node objects
   * @param {Array} edgesData - Array of edge objects
   * @param {Object} options - Network visualization options
   * @returns {Object} - Object containing network, nodes and edges datasets
   */
  createNetwork: function (container, nodesData, edgesData, options) {
    const nodes = new vis.DataSet(nodesData);
    const edges = new vis.DataSet(edgesData);

    const data = {
      nodes: nodes,
      edges: edges,
    };

    const network = new vis.Network(container, data, options);

    return { network, nodes, edges };
  },

  /**
   * Set up label configuration handlers
   * @param {DataSet} nodes - vis.js nodes dataset
   * @param {Object} nodeDataMap - Map of node IDs to node data
   */
  setupLabelHandlers: function (nodes, nodeDataMap) {
    // Function to update node labels based on selected options
    const updateNodeLabels = () => {
      const checkedOptions = Array.from(
        document.querySelectorAll(
          "#labelConfigForm input:checked:not([disabled])"
        )
      ).map((input) => input.value);

      // Update each node's label
      nodes.forEach((node) => {
        const nodeData = nodeDataMap[node.id];
        if (!nodeData) return;

        let label = [];
        // Always add name in bold
        if (nodeData.name) {
          label.push(`<b>${nodeData.name}</b>`);
        }

        // Add other selected properties
        checkedOptions.forEach((option) => {
          if (nodeData[option] && option !== "name") {
            label.push(`${nodeData[option]}`);
          }
        });

        nodes.update({
          id: node.id,
          label: label.join("\n"),
        });
      });
    };

    // Add event listeners to checkboxes
    document
      .querySelectorAll('#labelConfigForm input[type="checkbox"]')
      .forEach((checkbox) => {
        checkbox.addEventListener("change", updateNodeLabels);
      });

    // Initialize labels
    updateNodeLabels();
  },

  /**
   * Set up hover and blur effects
   * @param {Network} network - vis.js network instance
   * @param {DataSet} nodes - vis.js nodes dataset
   * @param {DataSet} edges - vis.js edges dataset
   */
  setupHoverEffects: function (network, nodes, edges, focusNodeId) {
    // Node hover handler
    network.on("hoverNode", function (params) {
      const hoveredNodeId = params.node;
      const connectedEdges = network.getConnectedEdges(hoveredNodeId);
      const connectedNodes = network.getConnectedNodes(hoveredNodeId);

      // Dim all nodes except hovered and connected
      nodes.getIds().forEach((nodeId) => {
        if (nodeId !== hoveredNodeId && !connectedNodes.includes(nodeId)) {
          // Skip the focus node - preserve its color
          if (focusNodeId && nodeId === focusNodeId) {
            return;
          }

          nodes.update({
            id: nodeId,
            color: {
              background: "#EEEEEE",
              border: "#CCCCCC",
            },
            opacity: 1,
          });
        }
      });

      // Process each connected edge
      connectedEdges.forEach((edgeId) => {
        const edgeData = edges.get(edgeId);

        if (edgeData.from === hoveredNodeId) {
          // Outgoing edge - highlight red
          edges.update({
            id: edgeId,
            color: "#E53935",
            width: 3,
            shadow: true,
          });
        } else if (edgeData.to === hoveredNodeId) {
          // Incoming edge - highlight green
          edges.update({
            id: edgeId,
            color: "#008000",
            width: 3,
            shadow: true,
          });
        }
      });
    });

    // Node blur handler
    network.on("blurNode", function () {
      // Restore all nodes to original colors
      nodes.getIds().forEach((nodeId) => {
        // Skip the focus node - preserve its color
        if (focusNodeId && nodeId === focusNodeId) {
          return;
        }
        nodes.update({
          id: nodeId,
          color: {
            border: "#2B7CE9",
            background: "#97C2FC",
          },
          opacity: 1,
        });
      });

      // Restore all edges to original colors
      edges.getIds().forEach((edgeId) => {
        edges.update({
          id: edgeId,
          color: "#848484",
          width: 1,
          shadow: false,
        });
      });
    });
  },

  /**
   * Set up node click handler
   * @param {Network} network - vis.js network instance
   */
  setupClickHandler: function (network) {
    network.on("click", function (params) {
      // Check if a node was clicked
      if (params.nodes && params.nodes.length > 0) {
        const nodeId = params.nodes[0];

        // Navigate to the focused view for this node
        window.location.href = `/plugins/praksis-nhn-nautobot/samband/graph/${nodeId}/`;
      }
    });
  },
};

/**
 * Initialize the network graph visualization
 * @param {string} containerId - ID of the container element
 * @returns {Object} - Object containing the network and related components
 */
function initNetworkGraph(containerId = "network-container") {
  return NetworkGraphRenderer.initialize(containerId);
}
