const DataService = {
  /**
   * Fetch hierarchy data from the API
   * @param {string} connectionId - ID of the current connection
   * @param {number} depth - Maximum depth to fetch
   * @returns {Promise} - Promise that resolves to the hierarchy data
   */
  fetchHierarchyData: function (connectionId) {
    const endpoint = `/api/plugins/praksis-nhn-nautobot/samband/${connectionId}/hierarchy/`;

    return fetch(endpoint).then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    });
  },

  /**
   * Extract direct (first-level) relations from relation data
   * @param {Array} relations - Array of relation objects
   * @returns {Array} - Array with only first-level relations
   */
  extractDirectRelations: function (relations) {
    if (!Array.isArray(relations)) return [];

    return relations.map((relation) => {
      // Create a shallow copy without nested relations
      const { parents, children, ...directRelation } = relation;
      return directRelation;
    });
  },
};

const GraphProcessor = {
  /**
   * Process API data into graph format suitable for D3
   * @param {Object|Array} data - API data to process
   * @param {string} mode - View mode: 'parents', 'children', or 'hierarchy'
   * @param {Object} config - Configuration object
   * @returns {Object} - Object with nodes and links arrays
   */
  processApiData: function (data, mode, config) {
    const { connectionId, connectionName, sambandsnummer, maxDepth } = config;

    const nodes = [];
    const links = [];

    // Add current connection as the root node
    const rootNode = {
      id: connectionId,
      name: connectionName,
      sambandsnummer: sambandsnummer,
      type: "current",
    };
    nodes.push(rootNode);

    switch (mode) {
      case "parents":
        if (Array.isArray(data)) {
          this.processRelationData(data, nodes, links, rootNode, true, 0, 0);
        }
        break;
      case "children":
        if (Array.isArray(data)) {
          this.processRelationData(data, nodes, links, rootNode, false, 0, 0);
        }
        break;
      case "hierarchy":
        if (data.parent_tree) {
          this.processRelationData(
            data.parent_tree,
            nodes,
            links,
            rootNode,
            true,
            0,
            maxDepth - 1
          );
        }
        if (data.child_tree) {
          this.processRelationData(
            data.child_tree,
            nodes,
            links,
            rootNode,
            false,
            0,
            maxDepth - 1
          );
        }
        break;
    }

    return { nodes, links };
  },

  /**
   * Process relation data recursively
   * @param {Array} relationData - Array of relation objects
   * @param {Array} nodes - Array to add nodes to
   * @param {Array} links - Array to add links to
   * @param {Object} connectedNode - The node these relations connect to
   * @param {boolean} isParent - True if these are parent relations, false for children
   * @param {number} currentDepth - Current recursion depth
   * @param {number} maxDepth - Maximum recursion depth
   */
  processRelationData: function (
    relationData,
    nodes,
    links,
    connectedNode,
    isParent,
    currentDepth = 0,
    maxDepth = Infinity
  ) {
    if (!relationData || !Array.isArray(relationData)) return;

    relationData.forEach((relation) => {
      // Ensure relation has an ID
      if (!relation || !relation.id) return;

      // Check if node already exists
      const existingNode = nodes.find((n) => n.id === relation.id);
      if (!existingNode) {
        nodes.push({
          id: relation.id,
          name: relation.name || "Unknown",
          sambandsnummer: relation.sambandsnummer || "",
          depth: relation.depth,
          type: isParent ? "parent" : "child",
        });
      }

      // Make sure connectedNode is valid and has an id
      if (!connectedNode || !connectedNode.id) return;

      // Add link if it doesn't exist
      this.addLinkIfNotExists(links, connectedNode, relation, isParent);

      // Only recurse if we haven't reached max depth
      if (currentDepth < maxDepth) {
        // Recursively process relation's relations
        const nextRelations = isParent ? relation.parents : relation.children;
        if (nextRelations) {
          this.processRelationData(
            nextRelations,
            nodes,
            links,
            {
              id: relation.id,
              name: relation.name || "Unknown",
              sambandsnummer: relation.sambandsnummer || "",
              type: isParent ? "parent" : "child",
            },
            isParent,
            currentDepth + 1,
            maxDepth
          );
        }
      }
    });
  },

  /**
   * Add a link to the links array if it doesn't exist already
   * @param {Array} links - Array of links
   * @param {Object} connectedNode - Source or target node
   * @param {Object} relation - Target or source node
   * @param {boolean} isParent - Direction of the relationship
   */
  addLinkIfNotExists: function (links, connectedNode, relation, isParent) {
    // Check if link already exists - handle both object and string references
    const linkExists = links.some((l) => {
      if (typeof l.source === "object" && typeof l.target === "object") {
        return isParent
          ? l.source.id === relation.id && l.target.id === connectedNode.id
          : l.source.id === connectedNode.id && l.target.id === relation.id;
      } else {
        return isParent
          ? l.source === relation.id && l.target === connectedNode.id
          : l.source === connectedNode.id && l.target === relation.id;
      }
    });

    if (!linkExists) {
      links.push({
        source: isParent ? relation.id : connectedNode.id,
        target: isParent ? connectedNode.id : relation.id,
        type: "parent-child",
      });
    }
  },
};

const GraphRenderer = {
  /**
   * Initialize the D3 graph visualization
   * @param {string} containerId - ID of the container element
   * @param {Object} graphData - Graph data with nodes and links
   * @param {Object} config - Configuration object
   * @returns {Object} - The created graph object
   */
  initializeGraph: function (containerId, graphData, config) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    if (graphData.nodes.length <= 1) {
      container.innerHTML =
        '<div class="alert alert-info">Ikke nok koblinger til å lage visning.</div>';
      return null;
    }

    const width = container.offsetWidth;
    const height = container.offsetHeight;

    const { connectionId, currentMode } = config;

    // Create SVG and D3 visualization
    const svg = this.createSvg(containerId, width, height);
    const g = svg.append("g");

    // Set up zoom behavior
    this.setupZoom(svg, g);

    // Create simulation
    const simulation = d3.forceSimulation(graphData.nodes).stop();

    // Draw links and nodes
    this.createArrowMarker(svg);
    const link = this.createLinks(g, graphData.links);
    const node = this.createNodes(g, graphData.nodes);

    // Create graph object
    const graph = {
      svg: svg,
      g: g,
      nodes: graphData.nodes,
      links: graphData.links,
      simulation: simulation,
      elements: {
        node: node,
        link: link,
      },
    };

    // Apply initial layout
    this.applyLayout(graph, connectionId, currentMode, width, height);

    return graph;
  },

  /**
   * Create the SVG element
   * @param {string} containerId - ID of the container element
   * @param {number} width - Width of the container
   * @param {number} height - Height of the container
   * @returns {Selection} - D3 selection of the created SVG
   */
  createSvg: function (containerId, width, height) {
    return d3
      .select(`#${containerId}`)
      .append("svg")
      .attr("width", width)
      .attr("height", height - 20)
      .style("overflow", "hidden")
      .style("display", "block")
      .style("margin", "0 auto");
  },

  /**
   * Set up zoom behavior
   * @param {Selection} svg - D3 selection of the SVG element
   * @param {Selection} g - D3 selection of the group element
   */
  setupZoom: function (svg, g) {
    const zoom = d3
      .zoom()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);
  },

  /**
   * Create arrow marker for directed links
   * @param {Selection} svg - D3 selection of the SVG element
   */
  createArrowMarker: function (svg) {
    svg
      .append("defs")
      .append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 20)
      .attr("refY", 0)
      .attr("orient", "auto")
      .attr("markerWidth", 8)
      .attr("markerHeight", 8)
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#999");
  },

  /**
   * Create links between nodes
   * @param {Selection} g - D3 selection of the group element
   * @param {Array} links - Array of link objects
   * @returns {Selection} - D3 selection of the created links
   */
  createLinks: function (g, links) {
    return g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#999")
      .attr("stroke-width", 1.5)
      .attr("marker-end", "url(#arrowhead)");
  },

  /**
   * Create node elements
   * @param {Selection} g - D3 selection of the group element
   * @param {Array} nodes - Array of node objects
   * @returns {Selection} - D3 selection of the created nodes
   */
  createNodes: function (g, nodes) {
    const node = g
      .append("g")
      .attr("class", "nodes")
      .selectAll(".node")
      .data(nodes)
      .enter()
      .append("g")
      .attr("class", "node");

    // Add circles
    node
      .append("circle")
      .attr("r", (d) => (d.type === "current" ? 18 : 14))
      .attr("fill", (d) => this.getNodeColor(d))
      .attr("stroke", (d) => (d.type === "current" ? "#fff" : "#ddd"))
      .attr("stroke-width", (d) => (d.type === "current" ? 3 : 2));

    // Add text and tooltips
    this.addNodeText(node);
    this.addNodeTooltips(node);

    // Add click handlers
    this.setupNodeClickHandlers(node);

    return node;
  },

  /**
   * Get the color for a node based on its type
   * @param {Object} d - Node data object
   * @returns {string} - Color string
   */
  getNodeColor: function (d) {
    switch (d.type) {
      case "current":
        return "#3498db";
      case "parent":
        return "#2ecc71";
      case "child":
        return "#e74c3c";
      default:
        return "#95a5a6";
    }
  },

  /**
   * Add text labels to nodes
   * @param {Selection} node - D3 selection of nodes
   */
  addNodeText: function (node) {
    node.each(function (d) {
      const textGroup = d3.select(this);
      const fullName = d.name || "";
      const fontSize = d.type === "current" ? 12 : 10;

      // Function to wrap text
      function wrapText(text, width) {
        // Split the text into words
        const words = text.split(/\s+/);
        let line = [];
        let lineNumber = 0;
        const lineHeight = fontSize * 1.2; // Line height based on font size

        let tspan = textGroup
          .append("text")
          .attr("text-anchor", "middle")
          .attr("dy", 30) // Position below circle
          .attr("fill", "#000") // Black text for better readability
          .style("font-size", `${fontSize}px`)
          .style("font-weight", d.type === "current" ? "bold" : "normal")
          .append("tspan")
          .attr("x", 0);

        words.forEach((word) => {
          line.push(word);
          const lineText = line.join(" ");
          tspan.text(lineText);

          // Check if the line is too long (rough approximation)
          if (lineText.length > width / (fontSize * 0.6)) {
            line.pop(); // Remove the last word
            tspan.text(line.join(" ")); // Set the text without the last word

            line = [word]; // Start a new line with the removed word
            lineNumber++;

            // Create a new tspan for the next line
            tspan = textGroup
              .append("text")
              .attr("text-anchor", "middle")
              .attr("dy", 30 + lineNumber * lineHeight) // Position each line below the previous
              .attr("fill", "#000")
              .style("font-size", `${fontSize}px`)
              .style("font-weight", d.type === "current" ? "bold" : "normal")
              .append("tspan")
              .attr("x", 0)
              .text(word);
          }
        });

        return lineNumber;
      }

      // Wrap the text with appropriate width based on node type
      const lineCount = wrapText(fullName, d.type === "current" ? 140 : 120);

      // Store line count for sambandsnummer positioning
      d.lineCount = lineCount;
    });

    // Add sambandsnummer below the name
    node
      .append("text")
      .text((d) => d.sambandsnummer || "")
      .attr("text-anchor", "middle")
      .attr("dy", (d) => {
        // Position below the name based on number of lines
        const baseOffset = 30;
        const lineHeight = d.type === "current" ? 14.4 : 12;
        const nameLines = d.lineCount || 0;

        return baseOffset + (nameLines + 1) * lineHeight;
      })
      .attr("fill", "#666")
      .style("font-size", (d) => (d.type === "current" ? "10px" : "9px"))
      .style("font-style", "italic");
  },

  /**
   * Add tooltips to nodes
   * @param {Selection} node - D3 selection of nodes
   */
  addNodeTooltips: function (node) {
    node
      .append("title")
      .text((d) => `${d.name || ""}\nSB-num: ${d.sambandsnummer || "N/A"}`);
  },

  /**
   * Set up click handlers for nodes
   * @param {Selection} node - D3 selection of nodes
   */
  setupNodeClickHandlers: function (node) {
    node.on("click", function (event, d) {
      if (d.id !== GraphApplication.config.connectionId) {
        window.location.href = `/plugins/praksis-nhn-nautobot/samband/${d.id}/graph`;
      }
    });
  },

  /**
   * Apply layout to the graph
   * @param {Object} graph - Graph object
   * @param {string} connectionId - ID of the current connection
   * @param {string} currentMode - Current view mode
   * @param {number} width - Width of the container
   * @param {number} height - Height of the container
   */
  applyLayout: function (graph, connectionId, currentMode, width, height) {
    const centerX = width / 2;
    const centerY = height / 2;
    const padding = 30;
    const spacing = 0.25;

    // Find and position the current node
    const currentNode = graph.nodes.find((n) => n.id === connectionId);
    currentNode.x = centerX;
    currentNode.y = centerY;
    currentNode.fx = centerX;
    currentNode.fy = centerY;

    // Apply the appropriate layout based on mode
    if (currentMode === "hierarchy") {
      this.applyHierarchicalLayout(
        graph,
        centerX,
        centerY,
        width,
        height,
        spacing
      );
    } else {
      this.applySimpleLayout(
        graph,
        centerX,
        centerY,
        width,
        height,
        spacing,
        currentMode
      );
    }

    // Validate and finalize positions
    this.finalizeNodePositions(graph, width, height, centerX, centerY, padding);

    // Update positions of visual elements
    this.updatePositions(graph, centerX, centerY);

    // Stop the simulation
    graph.simulation.stop();
  },

  /**
   * Apply hierarchical layout to the graph
   * @param {Object} graph - Graph object
   * @param {number} centerX - X coordinate of the center
   * @param {number} centerY - Y coordinate of the center
   * @param {number} width - Width of the container
   * @param {number} height - Height of the container
   * @param {number} spacing - Spacing factor
   */
  applyHierarchicalLayout: function (
    graph,
    centerX,
    centerY,
    width,
    height,
    spacing
  ) {
    if (!graph || !graph.nodes || !graph.links) return;

    // Find parent and child nodes
    const connectionId = GraphApplication.config.connectionId;
    const parents = graph.nodes.filter((n) => n.type === "parent");
    const children = graph.nodes.filter((n) => n.type === "child");

    // Create sets to track direct connections
    const directParentIds = new Set();
    const directChildIds = new Set();

    // Identify direct connections by analyzing links
    graph.links.forEach((link) => {
      // Handle links with object references
      if (typeof link.source === "object" && typeof link.target === "object") {
        // Direct parent: link from parent to current node
        if (link.target.id === connectionId) {
          directParentIds.add(link.source.id);
        }
        // Direct child: link from current node to child
        else if (link.source.id === connectionId) {
          directChildIds.add(link.target.id);
        }
      }
      // Handle links with string IDs
      else {
        // Direct parent: link from parent to current node
        if (link.target === connectionId) {
          directParentIds.add(link.source);
        }
        // Direct child: link from current node to child
        else if (link.source === connectionId) {
          directChildIds.add(link.target);
        }
      }
    });

    // Calculate radii for inner and outer rings
    const baseRadius = Math.min(width, height) * 0.3;
    const innerRadius = baseRadius;
    const outerRadius = baseRadius * 2;

    // Split parents and children into direct and indirect connections
    const directParents = parents.filter((n) => directParentIds.has(n.id));
    const indirectParents = parents.filter((n) => !directParentIds.has(n.id));
    const directChildren = children.filter((n) => directChildIds.has(n.id));
    const indirectChildren = children.filter((n) => !directChildIds.has(n.id));

    // Position direct parents in the upper inner semicircle
    if (directParents.length > 0) {
      this.positionNodesInArc(
        directParents,
        centerX,
        centerY,
        innerRadius,
        Math.PI * 1,
        Math.PI * 0
      );
    }

    // Position indirect parents in the upper outer semicircle
    if (indirectParents.length > 0) {
      this.positionNodesInArc(
        indirectParents,
        centerX,
        centerY,
        outerRadius,
        Math.PI * 1,
        Math.PI * 0
      );
    }

    // Position direct children in the lower inner semicircle
    if (directChildren.length > 0) {
      this.positionNodesInArc(
        directChildren,
        centerX,
        centerY,
        innerRadius,
        Math.PI * 2,
        Math.PI * 1
      );
    }

    // Position indirect children in the lower outer semicircle
    if (indirectChildren.length > 0) {
      this.positionNodesInArc(
        indirectChildren,
        centerX,
        centerY,
        outerRadius,
        Math.PI * 2,
        Math.PI * 1
      );
    }
  },

  /**
   * Apply simple layout to the graph
   * @param {Object} graph - Graph object
   * @param {number} centerX - X coordinate of the center
   * @param {number} centerY - Y coordinate of the center
   * @param {number} width - Width of the container
   * @param {number} height - Height of the container
   * @param {number} spacing - Spacing factor
   * @param {string} mode - Current view mode
   */
  applySimpleLayout: function (
    graph,
    centerX,
    centerY,
    width,
    height,
    spacing,
    mode
  ) {
    if (!graph || !graph.nodes || !graph.links) return;

    // Get nodes based on current mode (excluding the current node)
    const currentId = GraphApplication.config.connectionId;
    const relationNodes =
      mode === "parents"
        ? graph.nodes.filter((n) => n.type === "parent")
        : graph.nodes.filter((n) => n.type === "child");

    if (relationNodes.length === 0) return;

    // Set up parameters for the layout
    const radius = Math.min(width, height) * 0.35; // Radius for the circle

    if (mode === "parents") {
      // Position parent nodes in a semicircle above the current node
      this.positionNodesInArc(
        relationNodes,
        centerX,
        centerY,
        radius,
        Math.PI * 1, // Start angle (upper left)
        Math.PI * 0 // End angle (upper right)
      );
    } else {
      // Position child nodes in a semicircle below the current node
      this.positionNodesInArc(
        relationNodes,
        centerX,
        centerY,
        radius,
        Math.PI * 2, // Start angle (lower left)
        Math.PI * 1 // End angle (lower right)
      );
    }
  },

  /**
   * Position nodes in an arc
   * @param {Array} nodes - Array of node objects
   * @param {number} centerX - X coordinate of the center
   * @param {number} centerY - Y coordinate of the center
   * @param {number} radius - Radius of the arc
   * @param {number} startAngle - Start angle in radians
   * @param {number} endAngle - End angle in radians
   */
  positionNodesInArc: function (
    nodes,
    centerX,
    centerY,
    radius,
    startAngle,
    endAngle
  ) {
    nodes.forEach((node, i) => {
      const angle =
        startAngle + ((endAngle - startAngle) * (i + 1)) / (nodes.length + 1);
      node.x = centerX + radius * Math.cos(angle);
      node.y = centerY - radius * Math.sin(angle);
      node.fx = node.x;
      node.fy = node.y;
    });
  },

  /**
   * Finalize node positions with validation and constraints
   * @param {Object} graph - Graph object
   * @param {number} width - Width of the container
   * @param {number} height - Height of the container
   * @param {number} centerX - X coordinate of the center
   * @param {number} centerY - Y coordinate of the center
   * @param {number} padding - Padding from the edges
   */
  finalizeNodePositions: function (
    graph,
    width,
    height,
    centerX,
    centerY,
    padding
  ) {
    graph.nodes.forEach((node) => {
      if (!this.isValidNumber(node.x) || !this.isValidNumber(node.y)) {
        node.x = centerX + (Math.random() - 0.5) * 100;
        node.y = centerY + (Math.random() - 0.5) * 100;
      }

      // Add padding to keep nodes visible
      node.x = Math.max(padding, Math.min(width - padding, node.x));
      node.y = Math.max(padding, Math.min(height - padding, node.y));
      node.fx = node.x;
      node.fy = node.y;
    });
  },

  /**
   * Check if a value is a valid number
   * @param {any} value - Value to check
   * @returns {boolean} - True if value is a valid number
   */
  isValidNumber: function (value) {
    return typeof value === "number" && !isNaN(value) && isFinite(value);
  },

  /**
   * Update positions of visual elements
   * @param {Object} graph - Graph object
   * @param {number} centerX - X coordinate of the center
   * @param {number} centerY - Y coordinate of the center
   */
  updatePositions: function (graph, centerX, centerY) {
    const nodeElements = d3.selectAll(".node");
    const linkElements = d3.selectAll(".links line");

    // Update link positions
    linkElements
      .attr("x1", (d) => {
        return (
          d.source.x ||
          (typeof d.source === "string"
            ? graph.nodes.find((n) => n.id === d.source)?.x || centerX
            : centerX)
        );
      })
      .attr("y1", (d) => {
        return (
          d.source.y ||
          (typeof d.source === "string"
            ? graph.nodes.find((n) => n.id === d.source)?.y || centerY
            : centerY)
        );
      })
      .attr("x2", (d) => {
        return (
          d.target.x ||
          (typeof d.target === "string"
            ? graph.nodes.find((n) => n.id === d.target)?.x || centerX
            : centerX)
        );
      })
      .attr("y2", (d) => {
        return (
          d.target.y ||
          (typeof d.target === "string"
            ? graph.nodes.find((n) => n.id === d.target)?.y || centerY
            : centerY)
        );
      });

    // Update node positions
    nodeElements.attr("transform", (d) => {
      return `translate(${d.x}, ${d.y})`;
    });
  },
};

const GraphApplication = {
  config: null,
  state: {
    completeGraphData: null,
    currentGraph: null,
    maxDepth: 2,
    currentMode: "hierarchy",
  },

  /**
   * Initialize the application
   * @param {Object} config - Configuration object with initial settings
   * @returns {Object} - The application object
   */
  init: function (config) {
    this.config = {
      containerId: config.containerId || "connection-graph",
      connectionId: config.connectionId,
      connectionName: config.connectionName || "Unknown Connection",
      sambandsnummer: config.sambandsnummer || "",
    };

    // Set up UI event handlers
    this.setupEventHandlers();

    // Initial state setup
    this.updateButtonStyles();
    this.updateDepthButtonStyles();
    this.toggleDepthControls(this.state.currentMode);

    // Load initial data
    this.fetchAndRenderGraph(true);

    return this;
  },

  /**
   * Set up event handlers for UI elements
   */
  setupEventHandlers: function () {
    // Mode selection buttons
    document.getElementById("showParents").addEventListener("click", () => {
      this.state.currentMode = "parents";
      this.updateButtonStyles();
      this.toggleDepthControls(this.state.currentMode);
      this.renderCurrentView();
    });

    document.getElementById("showChildren").addEventListener("click", () => {
      this.state.currentMode = "children";
      this.updateButtonStyles();
      this.toggleDepthControls(this.state.currentMode);
      this.renderCurrentView();
    });

    document.getElementById("showHierarchy").addEventListener("click", () => {
      this.state.currentMode = "hierarchy";
      this.updateButtonStyles();
      this.toggleDepthControls(this.state.currentMode);
      this.renderCurrentView();
    });

    // Depth selection buttons
    const depthButtons = document.querySelectorAll(".depth-btn");
    depthButtons.forEach((button) => {
      button.addEventListener("click", () => {
        this.state.maxDepth = parseInt(button.getAttribute("data-depth"));
        this.updateDepthButtonStyles();
        this.fetchAndRenderGraph(true);
      });
    });
  },

  /**
   * Update button styles to match the current mode
   */
  updateButtonStyles: function () {
    document.getElementById("showParents").className =
      this.state.currentMode === "parents"
        ? "btn btn-primary"
        : "btn btn-default";

    document.getElementById("showChildren").className =
      this.state.currentMode === "children"
        ? "btn btn-primary"
        : "btn btn-default";

    document.getElementById("showHierarchy").className =
      this.state.currentMode === "hierarchy"
        ? "btn btn-primary"
        : "btn btn-default";
  },

  /**
   * Update depth button styles to match the current depth
   */
  updateDepthButtonStyles: function () {
    document.querySelectorAll(".depth-btn").forEach((btn) => {
      const depthValue = parseInt(btn.getAttribute("data-depth"));
      btn.className =
        depthValue === this.state.maxDepth
          ? "btn btn-primary depth-btn active"
          : "btn btn-default depth-btn";
    });
  },

  /**
   * Toggle visibility of depth controls based on mode
   * @param {string} mode - Current view mode
   */
  toggleDepthControls: function (mode) {
    const depthControls = document.getElementById("depth-controls");
    depthControls.style.display =
      mode === "hierarchy" ? "inline-block" : "none";
  },

  /**
   * Fetch graph data and render it
   * @param {boolean} forceReload - Whether to force reload data from API
   */
  fetchAndRenderGraph: function (forceReload = false) {
    if (this.state.completeGraphData && !forceReload) {
      this.renderCurrentView();
      return;
    }

    // Show loading indicator
    document.getElementById(this.config.containerId).innerHTML =
      '<div class="text-center"><i class="fa fa-spinner fa-spin fa-3x"></i><p>Laster grafvisning...</p></div>';

    // Fetch data from API
    DataService.fetchHierarchyData(
      this.config.connectionId,
      this.state.maxDepth
    )
      .then((data) => {
        this.state.completeGraphData = data;
        this.renderCurrentView();
      })
      .catch((error) => {
        console.error("API Error:", error);
        document.getElementById(
          this.config.containerId
        ).innerHTML = `<div class="alert alert-danger">Error loading graph data: ${error.message}</div>`;
      });
  },

  /**
   * Render the current view based on the current mode
   */
  renderCurrentView: function () {
    if (!this.state.completeGraphData) {
      console.error("No data available to render");
      return;
    }

    let dataToProcess;

    // Prepare data based on current mode
    switch (this.state.currentMode) {
      case "parents":
        // For parents view, only show direct connections
        dataToProcess = DataService.extractDirectRelations(
          this.state.completeGraphData.parent_tree || []
        );
        break;

      case "children":
        // For children view, only show direct connections
        dataToProcess = DataService.extractDirectRelations(
          this.state.completeGraphData.child_tree || []
        );
        break;

      case "hierarchy":
        // For hierarchy view, use the complete data
        dataToProcess = this.state.completeGraphData;
        break;
    }

    // Process the data for visualization
    const graphData = GraphProcessor.processApiData(
      dataToProcess,
      this.state.currentMode,
      {
        connectionId: this.config.connectionId,
        connectionName: this.config.connectionName,
        sambandsnummer: this.config.sambandsnummer,
        maxDepth: this.state.maxDepth,
      }
    );

    // Render the processed data
    this.state.currentGraph = GraphRenderer.initializeGraph(
      this.config.containerId,
      graphData,
      {
        connectionId: this.config.connectionId,
        currentMode: this.state.currentMode,
      }
    );
  },
};

// Add this at the end of your graph_view.js file
// Global initialization function
function initGraphView(config) {
  return GraphApplication.init(config);
}
