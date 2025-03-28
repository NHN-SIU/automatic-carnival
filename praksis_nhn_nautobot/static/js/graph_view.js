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
    const link = this.createLinks(g, graphData.links, connectionId);
    const node = this.createNodes(g, graphData.nodes, connectionId);

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
  createNodes: function (g, nodes, connectionId) {
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
    this.setupNodeClickHandlers(node, connectionId);

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
  setupNodeClickHandlers: function (node, connectionId) {
    node.on("click", function (event, d) {
      if (d.id !== connectionId) {
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
        connectionId,
        centerX,
        centerY,
        width,
        height,
        spacing
      );
    } else {
      this.applySimpleLayout(
        graph,
        connectionId,
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
    connectionId,
    centerX,
    centerY,
    width,
    height,
    spacing
  ) {
    if (!graph || !graph.nodes || !graph.links) return;

    // Find parent and child nodes
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
    connectionId,
    centerX,
    centerY,
    width,
    height,
    spacing,
    mode
  ) {
    if (!graph || !graph.nodes || !graph.links) return;

    // Get nodes based on current mode (excluding the current node)
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

function initGraphView(config) {
  console.log;
  console.log(config);

  const container = document.getElementById(config.containerId);
  container.innerHTML = "";

  if (config.connectionId) {
    // Fetch data from API if only connectionId is provided
    container.innerHTML = '<div class="loading">Loading graph data...</div>';

    const url = `/api/plugins/praksis-nhn-nautobot/samband/${
      config.connectionId
    }/hierarchy/?depth=${config.depth || 2}`;

    fetch(url)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Network response was not ok (${response.status})`);
        }
        return response.json();
      })
      .then((data) => {
        container.innerHTML = "";
        GraphRenderer.initializeGraph(config.containerId, data.graph_data, {
          connectionId: config.connectionId,
          connectionName: data.samband.name,
          currentMode: config.mode || "hierarchy",
        });
      })
      .catch((error) => {
        container.innerHTML = `<div class="alert alert-danger">Error loading graph data: ${error.message}</div>`;
        console.error("Error loading graph data:", error);
      });
  } else {
    container.innerHTML =
      '<div class="alert alert-warning">Missing connection data</div>';
  }

  return true;
}
