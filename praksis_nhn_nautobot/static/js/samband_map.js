document.addEventListener('DOMContentLoaded', function() {
    // Global variables
    let map, pointsLayer, connectionsLayer, radiusLayer;
    let activeMarker = null;
    let activeLines = [];
    let previouslyActiveMarkers = [];
    let featureIdToMarkers = {};
    let featureIdToLines = {};
    let locationMarker = null;
    let radiusMarker = null;
    let currentRadius = 0;
    let targetRadius = 0;
    let animationInProgress = false;
    let pinPlacementMode = false;
    let selectedConnectionId = null;
    let searchTimeout = null;
    let selectedSuggestionIndex = -1;
    let last_used_params = null;
    
    // Status color mapping
    const statusColors = {
      'Active': '#4CAF50',     // Green
      'Planned': '#FFC107',    // Yellow
      'Decommissioned': '#F44336', // Red
      'Unknown': '#9E9E9E'     // Grey (fallback)
    };
    
    // Location type icon mapping
    const locationTypeIcons = {
      'Hospital': {
        icon: 'fa-solid fa-hospital',
        color: '#E91E63',
        size: [24, 24]
      },
      'Data Center': {
        icon: 'fa-solid fa-server',
        color: '#673AB7',
        size: [24, 24]
      },
      'Pharmacy': {
        icon: 'fa-solid fa-prescription-bottle-medical',
        color: '#009688',
        size: [24, 24]
      },
      'Primary Care': {
        icon: 'fa-solid fa-user-doctor',
        color: '#FF5722',
        size: [24, 24]
      },
      'Medical Imaging': {
        icon: 'fa-solid fa-x-ray',
        color: '#8BC34A',
        size: [24, 24]
      }
    };
    
    // Initialize map
    initializeMap();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Load initial data
    loadMapData(getURLParameters());
    
    // Set up legend toggle functionality
    document.getElementById('toggle-legend').addEventListener('click', function() {
      const legend = document.querySelector('.map-legend');
      legend.classList.toggle('collapsed');
      
      // Store preference in localStorage
      localStorage.setItem('map_legend_collapsed', legend.classList.contains('collapsed'));
    });
    
    // Check if legend was collapsed in previous session
    function initLegendState() {
      const wasCollapsed = localStorage.getItem('map_legend_collapsed');
      if (wasCollapsed === 'true') {
        document.querySelector('.map-legend').classList.add('collapsed');
      }
    }
    
    // Call this at the end of your initialization
    initLegendState();
    
    /**
     * Initialize the map and layers
     */
    function initializeMap() {
      // Create the map
      map = new L.Map('leaflet', {
        center: [65.4, 17.0],
        zoom: 6,
        preferCanvas: true
      });
  
      // Add basemap layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);
  
      // Layer groups
      pointsLayer = L.layerGroup().addTo(map);
      connectionsLayer = L.layerGroup().addTo(map);
      radiusLayer = L.layerGroup().addTo(map);
      
      // Populate location type legend
      populateLocationTypeLegend();
      // initLegendState();
    }
    
    /**
     * Populate legend with location type icons
     */
    function populateLocationTypeLegend() {
      const locationTypeLegend = document.getElementById('location-type-legend');
      for (const [type, config] of Object.entries(locationTypeIcons)) {
        const item = document.createElement('div');
        item.className = 'legend-item';
        
        item.innerHTML = `
          <div style="width: 16px; margin-right: 5px; text-align: center;">
            <i class="${config.icon}" style="color: ${config.color}; font-size: 12px;"></i>
          </div>
          <span>${type}</span>
        `;
        
        locationTypeLegend.appendChild(item);

      }
      const wasCollapsed = localStorage.getItem('map_legend_collapsed');
      if (wasCollapsed === 'true') {
        document.querySelector('.map-legend').classList.add('collapsed');
      }
    }
    
    /**
     * Create a custom icon for a location type
     */
    function createLocationIcon(locationType) {
      const config = locationTypeIcons[locationType] || {
        icon: 'fa-solid fa-location-dot',
        color: '#3186cc',
        size: [24, 24]
      };
      
      return L.divIcon({
        html: `<div style="background-color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                <i class="${config.icon}" style="color: ${config.color}; font-size: 14px;"></i>
              </div>`,
        className: '',
        iconSize: config.size,
        iconAnchor: [12, 12],
        popupAnchor: [0, -12]
      });
    }
    
    /**
     * Get color for connection status
     */
    function getStatusColor(status) {
      return statusColors[status] || statusColors['Unknown'];
    }
  
    /**
     * Reset all active elements (highlighted connections)
     */
    function resetActiveElements() {
      if (selectedConnectionId) {
        // Reset all previously active markers
        if (featureIdToMarkers[selectedConnectionId]) {
          featureIdToMarkers[selectedConnectionId].forEach(function(marker) {
            // Reset marker icon size or style
            const icon = marker.getIcon();
            icon.options.html = icon.options.html.replace('width: 32px; height: 32px', 'width: 24px; height: 24px')
                                                .replace('font-size: 18px', 'font-size: 14px');
            icon.options.iconSize = [24, 24];
            icon.options.iconAnchor = [12, 12];
            marker.setIcon(icon);
          });
        }
        
        // Reset active lines
        if (featureIdToLines[selectedConnectionId]) {
          featureIdToLines[selectedConnectionId].forEach(function(line) {
            // Use status-based color with opacity
            const statusColor = getStatusColor(line.options.status || 'Unknown');
            line.setStyle({
              color: statusColor,
              weight: 2.5,
              opacity: 0.8
            });
          });
        }
      }
      
      selectedConnectionId = null;
      activeMarker = null;
      activeLines = [];
    }
  
    /**
     * Highlight a connection on the map
     */
    function highlightConnection(connectionId) {
      selectedConnectionId = connectionId;
      if (featureIdToMarkers[connectionId]) {
        featureIdToMarkers[connectionId].forEach(function(marker) {
          // Increase icon size for highlighting
          const icon = marker.getIcon();
          
          // Update both the icon size AND the icon anchor point
          icon.options.html = icon.options.html.replace('width: 24px; height: 24px', 'width: 32px; height: 32px')
                                            .replace('font-size: 14px', 'font-size: 18px');
          
          // Update the icon anchor to center the larger icon
          icon.options.iconSize = [32, 32];    // Update to match new size
          icon.options.iconAnchor = [16, 16];  // Center point of the new size
          
          marker.setIcon(icon);
          marker.setZIndexOffset(10); // Bring to front
        });
      }
      
      if (featureIdToLines[connectionId]) {
        featureIdToLines[connectionId].forEach(function(line) {
          line.setStyle({
            color: '#0000FF',  // Blue line for selected connections
            weight: 4,
            opacity: 0.8
          });
          line.bringToFront();
          activeLines.push(line);
        });
      }
    }
  
    /**
     * Process map data and create markers and lines
     */
    function processMapData(data) {
      document.getElementById('connection-count').textContent = 
        `${data.count || 0} connection${data.count !== 1 ? 's' : ''}`;
      
      pointsLayer.clearLayers();
      connectionsLayer.clearLayers();
      radiusLayer.clearLayers();
      
      if (data.connections && data.connections.length > 0) {
        var bounds = [];
        
        data.connections.forEach(function(connection) {
          const connectionId = connection.id;
          const pointA = connection.point_a || {};
          const pointB = connection.point_b || {};
          const status = connection.status || 'Unknown';
          const locationType = connection.location_type || 'Unknown';
          
          // Skip if either point doesn't have location data
          if (!pointA.location || !pointB.location) {
            console.warn(`Connection ${connectionId} is missing location data:`, connection);
            return;
          }
          
          // Determine colors for status
          const statusColor = getStatusColor(status);
          
          // Create Point A marker with icon
          var markerA = L.marker(pointA.location, {
            icon: createLocationIcon(locationType)
          });
          
          markerA.bindTooltip(connection.name);
          markerA.on('click', function() {
            resetActiveElements();
            
            // Show popup
            fetchConnectionDetails(connectionId, function(details) {
              if (details.error) return;
              
              var popupContent = `
              <div style="min-width: 200px; max-width: 250px;">
                <strong>${connection.name} - Point A</strong><br>
                <strong>Status:</strong> ${status}<br>
                <strong>Bandwidth:</strong> ${details.bandwidth || 'N/A'}<br>
                <strong>Vendor:</strong> ${details.vendor || 'N/A'}<br>
                <strong>Type:</strong> ${details.type_name || 'N/A'}<br>
                <a href="/plugins/praksis-nhn-nautobot/samband/map/${connectionId}/" class="btn btn-primary btn-xs" style="color: white; font-size: 11px; padding: 2px 5px; margin-top: 5px;">View Details</a>
              </div>
              `;
                
              markerA.bindPopup(popupContent).openPopup();
              highlightConnection(connectionId);
            });
          });
          
          // Create Point B marker with icon
          var markerB = L.marker(pointB.location, {
            icon: createLocationIcon(locationType)
          });
          
          markerB.bindTooltip(connection.name);
          markerB.on('click', function() {
            resetActiveElements();
            
            // Show popup
            fetchConnectionDetails(connectionId, function(details) {
              if (details.error) return;
              
              var popupContent = `
              <div style="min-width: 200px; max-width: 250px;">
                <strong>${connection.name} - Point B</strong><br>
                <strong>Status:</strong> ${status}<br>
                <strong>Bandwidth:</strong> ${details.bandwidth || 'N/A'}<br>
                <strong>Vendor:</strong> ${details.vendor || 'N/A'}<br>
                <strong>Type:</strong> ${details.type_name || 'N/A'}<br>
                <a href="/plugins/praksis-nhn-nautobot/samband/map/${connectionId}/" class="btn btn-primary btn-xs" style="color: white; font-size: 11px; padding: 2px 5px; margin-top: 5px;">View Details</a>
              </div>
              `;
              
              markerB.bindPopup(popupContent).openPopup();
              highlightConnection(connectionId);
            });
          });
          
          // Create connection line with status-based color
          var line = L.polyline([pointA.location, pointB.location], {
            color: statusColor,
            weight: 2.5,
            opacity: 0.8,
            smoothFactor: 1,
            status: status
          });
          
          line.bindTooltip(connection.name);
          line.on('click', function(e) {
            resetActiveElements();
            
            // Show popup
            fetchConnectionDetails(connectionId, function(details) {
              if (details.error) return;
              
              var popupContent = `
              <div style="min-width: 200px; max-width: 250px;">
                <strong>${connection.name}</strong><br>
                <strong>Status:</strong> ${status}<br>
                <strong>Bandwidth:</strong> ${details.bandwidth || 'N/A'}<br>
                <strong>Vendor:</strong> ${details.vendor || 'N/A'}<br>
                <strong>Type:</strong> ${details.type_name || 'N/A'}<br>
                <a href="/plugins/praksis-nhn-nautobot/samband/map/${connectionId}/" class="btn btn-primary btn-xs" style="color: white; font-size: 11px; padding: 2px 5px; margin-top: 5px;">View Details</a>
              </div>
              `;
              
              // First unbind any existing popup
              line.unbindPopup();
              highlightConnection(connectionId);
              
              L.popup()
                .setLatLng(e.latlng)
                .setContent(popupContent)
                .openOn(map);
            });
          });
          
          // Store references for highlighting
          if (!featureIdToMarkers[connectionId]) featureIdToMarkers[connectionId] = [];
          featureIdToMarkers[connectionId].push(markerA, markerB);
          
          if (!featureIdToLines[connectionId]) featureIdToLines[connectionId] = [];
          featureIdToLines[connectionId].push(line);
          
          // Add to map
          markerA.addTo(pointsLayer);
          markerB.addTo(pointsLayer);
          line.addTo(connectionsLayer);
          
          // Track bounds for fitting view
          bounds.push(pointA.location);
          bounds.push(pointB.location);
        });
        
        // Fit map to bounds
        if (bounds.length > 0) map.fitBounds(bounds);
      } else {
        console.warn("Damn.. No connections found.");
      }
      
      // Add radius circle if specified
      if (data.radius) {
        radiusMarker = L.circle(data.radius.location, {
          radius: data.radius.radius_km * 1000,
          color: '#ff7800',
          weight: 1,
          fillColor: '#ff7800',
          fillOpacity: 0.2,
        }).addTo(radiusLayer);
        currentRadius = data.radius.radius_km;
      }
      
      // Update the connections list with the data
      updateConnectionsList(data.connections || []);
    }
  
    /**
     * Update the connections list in the sidebar
     */
    function updateConnectionsList(connections) {
      const listEl = document.getElementById('connections-list');
      const countEl = document.getElementById('list-connection-count');
      
      countEl.textContent = connections.length;
      
      if (connections.length === 0) {
        listEl.innerHTML = '<tr><td colspan="2" class="text-center p-3 text-muted">No connections to display</td></tr>';
        return;
      }
      
      let html = '';
      connections.forEach(connection => {
        const statusColor = getStatusColor(connection.status || 'Unknown');
        
        html += `
          <tr data-id="${connection.id}" class="connection-row">
            <td>${connection.name}</td>
            <td>
              <div style="display: flex; align-items: center;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${statusColor}; margin-right: 5px;"></span>
                ${connection.status || 'Unknown'}
              </div>
            </td>
          </tr>
        `;
      });
      
      listEl.innerHTML = html;
      
      // Add click handlers to rows
      document.querySelectorAll('.connection-row').forEach(row => {
        row.addEventListener('click', function() {
          const connectionId = this.dataset.id;
          resetActiveElements();
          highlightConnection(connectionId);
          highlightConnectionInList(connectionId);
          
          // Zoom to fit both points of the connection
          if (featureIdToMarkers[connectionId] && featureIdToMarkers[connectionId].length >= 2) {
            const bounds = L.latLngBounds();
            featureIdToMarkers[connectionId].forEach(marker => {
              bounds.extend(marker.getLatLng());
            });
            
            // Add a small padding to the bounds
            map.fitBounds(bounds, {
              padding: [50, 50],
              maxZoom: 14
            });
          }
        });
      });
    }
  
    /**
     * Highlight a connection in the sidebar list
     */
    function highlightConnectionInList(connectionId) {
      document.querySelectorAll('#connections-list tr').forEach(row => {
        if (row.dataset.id === connectionId) {
          row.classList.add('table-primary');
          
          // Scroll to the row
          row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
          row.classList.remove('table-primary');
        }
      });
    }
  
    /**
     * Highlight a connection by its ID
     */
    function highlightConnectionById(connectionId) {
      // First, check if the connection is already on the map
      if (featureIdToMarkers[connectionId]) {
        resetActiveElements();
        highlightConnection(connectionId);
        
        // Find the row in connections list and highlight it
        highlightConnectionInList(connectionId);
        
        // Create bounds to fit both points of the connection
        if (featureIdToMarkers[connectionId].length >= 2) {
          const bounds = L.latLngBounds();
          featureIdToMarkers[connectionId].forEach(marker => {
            bounds.extend(marker.getLatLng());
          });
          
          map.fitBounds(bounds, {
            padding: [50, 50],
            maxZoom: 14
          });
        }
        
        return true;
      }
      
      // If not on map, fetch it specifically
      document.getElementById('loading-indicator').style.display = 'block';
      
      fetch(`/plugins/praksis-nhn-nautobot/api/samband/map-data/?connection_id=${connectionId}`)
        .then(response => response.json())
        .then(data => {
          // Clear existing connections but keep radius if present
          const radiusData = {};
          if (radiusMarker) {
            const latLng = radiusMarker.getLatLng();
            radiusData.location = [latLng.lat, latLng.lng];
            radiusData.radius_km = currentRadius;
          }
          
          resetActiveElements();
          pointsLayer.clearLayers();
          connectionsLayer.clearLayers();
          
          // Process this single connection as if it came from normal data loading
          processMapData({
            connections: [{
              id: connectionId,
              name: data.name,
              status: data.status,
              location: data.location,
              city: data.city,
              location_type: data.location_type,
              point_a: {
                location: data.pop_a_coords,
                category: data.pop_a_category,
                city: data.pop_a_city
              },
              point_b: {
                location: data.pop_b_coords,
                category: data.pop_b_category,
                city: data.pop_b_city
              }
            }],
            count: 1,
            radius: radiusData.location ? radiusData : null
          });
          
          // After adding, highlight it
          highlightConnection(connectionId);
          highlightConnectionInList(connectionId);
          
          // Properly zoom to show both points
          if (featureIdToMarkers[connectionId] && featureIdToMarkers[connectionId].length >= 2) {
            const bounds = L.latLngBounds();
            featureIdToMarkers[connectionId].forEach(marker => {
              bounds.extend(marker.getLatLng());
            });
            map.fitBounds(bounds, {
              padding: [50, 50],
              maxZoom: 14
            });
          }
        })
        .catch(error => {
          console.error("Error fetching connection:", error);
        })
        .finally(() => {
          document.getElementById('loading-indicator').style.display = 'none';
        });
    }
  
    /**
     * Fetch connection details from the API
     */
    function fetchConnectionDetails(connectionId, callback) {
      fetch(`/plugins/praksis-nhn-nautobot/api/samband/map-data/?connection_id=${connectionId}`)
        .then(response => response.json())
        .then(data => {
          console.log("Connection details received:", data);
          callback(data);
        })
        .catch(error => {
          console.error("Error fetching connection details:", error);
          callback({ error: 'Could not load connection details' });
        });
    }
  
    /**
     * Load map data from the API
     */
    function loadMapData(params) {
      resetActiveElements();
      featureIdToMarkers = {};
      featureIdToLines = {};
      
      document.getElementById('loading-indicator').style.display = 'block';
      document.getElementById('connection-count').textContent = 'Loading...';
      
      let url = '/plugins/praksis-nhn-nautobot/api/samband/map-data/';
      if (params) {
        url += '?' + params;
        console.log("Loading map data with params:", params);
      }
      
      console.log("URL:", url);
      fetch(url)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Network response was not ok (${response.status})`);
          }
          return response.json();
        })
        .then(data => {
          // Store the current params
          last_used_params = params;
          console.log("last used params:", last_used_params);
          
          // Update all navigation links with current params
          updateNavigationLinks();
          
          console.log(`Received ${data.count} connections:`, data);
          processMapData(data);
        })
        .catch(error => {
          console.error("Error loading map data:", error);
          document.getElementById('connection-count').textContent = '0 connections';
        })
        .finally(() => {
          document.getElementById('loading-indicator').style.display = 'none';
        });
    }
  
    /**
     * Update links to maintain filter parameters across different views
     */
    function updateNavigationLinks() {
      const params = last_used_params || '';
      
      // Update the "Back to List" link
      const listLink = document.getElementById('back-to-list-link');
      if (listLink) {
        const listBaseUrl = listLink.getAttribute('href').split('?')[0];
        listLink.href = params ? `${listBaseUrl}?${params}` : listBaseUrl;
      }
      
      // Update the "View selection in graph" link
      const graphLink = document.querySelector('a[href*="samband_graph"]');
      if (graphLink) {
        const graphBaseUrl = graphLink.getAttribute('href').split('?')[0];
        graphLink.href = params ? `${graphBaseUrl}?${params}` : graphBaseUrl;
        graphLink.id = 'graph-view-link'; // Add an ID for easier future reference
      }
      
      console.log("Updated navigation links with params:", params);
    }
  
    /**
     * Remove pin from map
     */
    function remove_pin() {
      if (locationMarker) {
        map.removeLayer(locationMarker);
        locationMarker = null;
      }
        
      if (radiusMarker) {
        radiusLayer.clearLayers();
        radiusMarker = null;
      }
      
      const pinToggleBtn = document.getElementById('pin-toggle');
      pinToggleBtn.textContent = 'Place Pin on Map';
      pinToggleBtn.classList.remove('btn-outline-danger');
      pinToggleBtn.classList.add('btn-outline-primary');
      pinPlacementMode = false;
    }
  
    /**
     * Animate radius circle change
     */
    function animateRadiusChange() {
      if (!radiusMarker || currentRadius === targetRadius) {
        animationInProgress = false;
        return;
      }
      
      animationInProgress = true;
      const step = Math.max(0.5, Math.abs(targetRadius - currentRadius) * 0.1);
      
      if (currentRadius < targetRadius) {
        currentRadius = Math.min(targetRadius, currentRadius + step);
      } else {
        currentRadius = Math.max(targetRadius, currentRadius - step);
      }
      
      radiusMarker.setRadius(currentRadius * 1000);
      
      if (Math.abs(currentRadius - targetRadius) > 0.1) {
        requestAnimationFrame(animateRadiusChange);
      } else {
        currentRadius = targetRadius;
        radiusMarker.setRadius(currentRadius * 1000);
        animationInProgress = false;
      }
    }
  
    /**
     * Update radius circle on the map
     */
    function update_radius_circle(lat, lng, radiusKm) {
      radiusKm = parseFloat(radiusKm) || 50;
      targetRadius = radiusKm;
      
      if (!radiusMarker) {
        currentRadius = 0;
        radiusMarker = L.circle([lat, lng], {
          radius: 0,
          color: '#ff7800',
          weight: 1,
          fillColor: '#ff7800',
          fillOpacity: 0.2,
        }).addTo(radiusLayer);
        
        animateRadiusChange();
      } else {
        radiusMarker.setLatLng([lat, lng]);
        
        if (!animationInProgress) {
          animateRadiusChange();
        }
      }
    }
  
    /**
     * Update position point on the map
     */
    function update_pos_point_to_map(lat, lng, radiusKm) {
      if (!locationMarker) {
        locationMarker = L.marker([lat, lng], {
          draggable: true,
          icon: L.divIcon({
            className: 'location-marker',
            html: '<div style="position: absolute; top: -7px; left: -7px; background-color: #ff7800; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #000000;"></div>',
            iconSize: [0, 0],
            iconAnchor: [0, 0]
          })
        }).addTo(map);
        
        // Setup drag handler
        locationMarker.on('drag', function(event) {
          const position = event.target.getLatLng();
          document.getElementById('lat').value = position.lat.toFixed(6);
          document.getElementById('lng').value = position.lng.toFixed(6);
          const currentRadiusKm = parseFloat(document.getElementById('radius').value) || 50;
          update_radius_circle(position.lat, position.lng, currentRadiusKm);
        });
        
        const pinToggleBtn = document.getElementById('pin-toggle');
        pinToggleBtn.textContent = 'Remove Pin';
        pinToggleBtn.classList.remove('btn-outline-info', 'btn-outline-primary');
        pinToggleBtn.classList.add('btn-outline-danger');
      } else {
        locationMarker.setLatLng([lat, lng]);
      }
      
      update_radius_circle(lat, lng, radiusKm);
    }
  
    /**
     * Update from coordinate inputs
     */
    function updateFromCoordinateInputs() {
      const lat = parseFloat(document.getElementById('lat').value);
      const lng = parseFloat(document.getElementById('lng').value);
      const radiusKm = parseFloat(document.getElementById('radius').value) || 50;
      
      if (!isNaN(lat) && !isNaN(lng)) {
        update_pos_point_to_map(lat, lng, radiusKm);
      }
    }
  
    /**
     * Fetch search suggestions from API
     */
    function fetchSearchSuggestions(query) {
      document.getElementById('search-suggestions').innerHTML = '<div style="padding: 8px 12px; text-align: center;"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
      document.getElementById('search-suggestions').style.display = 'block';
  
      fetch(`/plugins/praksis-nhn-nautobot/api/samband/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Network response error: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          const suggestionsEl = document.getElementById('search-suggestions');
          
          if (!data.suggestions || data.suggestions.length === 0) {
            suggestionsEl.innerHTML = '<div style="padding: 8px 12px; color: #6c757d;">No matches found</div>';
            return;
          }
          
          // Build suggestions HTML
          let suggestionsHTML = '';
          data.suggestions.forEach(suggestion => {
            const statusColor = statusColors[suggestion.status] || '#9E9E9E';
            
            suggestionsHTML += `
              <div class="suggestion-item" data-id="${suggestion.id}"
                   style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #eee;">
                <div style="font-weight: 500;">${suggestion.name}</div>
                <div style="display: flex; font-size: 12px; color: #6c757d;">
                  <span style="margin-right: 8px;">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: ${statusColor};"></span>
                    ${suggestion.status || 'Unknown'}
                  </span>
                  <span>${suggestion.location || ''}</span>
                </div>
              </div>
            `;
          });
          
          // Update and display suggestions
          suggestionsEl.innerHTML = suggestionsHTML;
          suggestionsEl.style.display = 'block';
          selectedSuggestionIndex = -1;
          
          // Add click handlers to suggestions
          suggestionsEl.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
              const connectionId = this.dataset.id;
              document.getElementById('connection-search').value = this.querySelector('div:first-child').textContent.trim();
              suggestionsEl.style.display = 'none';
              highlightConnectionById(connectionId);
            });
            
            item.addEventListener('mouseover', function() {
              const items = suggestionsEl.querySelectorAll('.suggestion-item');
              for (let i = 0; i < items.length; i++) {
                if (items[i] === this) {
                  selectedSuggestionIndex = i;
                  highlightSuggestion(i);
                  break;
                }
              }
            });
          });
        })
        .catch(error => {
          console.error("Error fetching search suggestions:", error);
          document.getElementById('search-suggestions').innerHTML = 
            '<div style="padding: 8px 12px; color: #dc3545;">Error loading suggestions</div>';
        });
    }
  
    /**
     * Highlight selected suggestion
     */
    function highlightSuggestion(index) {
      const suggestionsEl = document.getElementById('search-suggestions');
      const suggestions = suggestionsEl.querySelectorAll('.suggestion-item');
      
      for (let i = 0; i < suggestions.length; i++) {
        if (i === index) {
          suggestions[i].style.backgroundColor = '#f0f0f0';
        } else {
          suggestions[i].style.backgroundColor = 'white';
        }
      }
    }
  
    /**
     * Get URL parameters
     */
    function getURLParameters() {
      const queryString = window.location.search;
      return queryString.startsWith('?') ? queryString.substring(1) : '';
    }
    
    /**
     * Set up all event handlers
     */
    function setupEventHandlers() {
      // Search input
      document.getElementById('connection-search').addEventListener('input', function() {
        const searchValue = this.value.trim();
        clearTimeout(searchTimeout);
        
        if (searchValue.length < 2) {
          document.getElementById('search-suggestions').style.display = 'none';
          return;
        }
        
        // Debounce to prevent too many requests
        searchTimeout = setTimeout(() => {
          fetchSearchSuggestions(searchValue);
        }, 300);
      });
      
      // Keyboard navigation for suggestions
      document.getElementById('connection-search').addEventListener('keydown', function(e) {
        const suggestionsEl = document.getElementById('search-suggestions');
        const suggestions = suggestionsEl.querySelectorAll('.suggestion-item');
        
        if (suggestionsEl.style.display === 'none') {
          if (e.key === 'Enter') {
            // Apply filters when Enter is pressed without suggestions visible
            document.getElementById('apply-filters').click();
          }
          return;
        }
        
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestions.length - 1);
          highlightSuggestion(selectedSuggestionIndex);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
          highlightSuggestion(selectedSuggestionIndex);
        } else if (e.key === 'Enter') {
          e.preventDefault();
          if (selectedSuggestionIndex >= 0) {
            suggestions[selectedSuggestionIndex].click();
          } else {
            // Apply filters when Enter is pressed without selecting a suggestion
            document.getElementById('apply-filters').click();
          }
        } else if (e.key === 'Escape') {
          suggestionsEl.style.display = 'none';
        }
      });
  
      // Hide suggestions when clicking elsewhere
      document.addEventListener('click', function(e) {
        if (!e.target.closest('#connection-search') && !e.target.closest('#search-suggestions')) {
          document.getElementById('search-suggestions').style.display = 'none';
        }
      });
  
      // Map click handler
      map.on('click', function(e) {
        if (!pinPlacementMode) {
          resetActiveElements();
        } else {
          // Place pin mode
          currentRadius = 0;
          const lat = e.latlng.lat;
          const lng = e.latlng.lng;
          const radiusKm = parseFloat(document.getElementById('radius').value) || 50;
          
          document.getElementById('lat').value = lat.toFixed(6);
          document.getElementById('lng').value = lng.toFixed(6);
          
          update_pos_point_to_map(lat, lng, radiusKm);
          
          const pinToggleBtn = document.getElementById('pin-toggle');
          pinToggleBtn.textContent = 'Remove Pin';
          pinToggleBtn.classList.remove('btn-outline-info', 'btn-outline-primary');
          pinToggleBtn.classList.add('btn-outline-danger');
          pinPlacementMode = false;
        }
      });
  
      // Pin toggle button
      document.getElementById('pin-toggle').addEventListener('click', function() {
        if (locationMarker) {
          remove_pin();
        } else {
          this.textContent = 'Click Map to Place Pin';
          this.classList.remove('btn-outline-primary');
          this.classList.add('btn-outline-info');
          pinPlacementMode = true;
        }
      });
  

      // Apply filters button
      document.getElementById('apply-filters').addEventListener('click', function() {
        const params = new URLSearchParams();
        
        const lat = document.getElementById('lat').value;
        const lng = document.getElementById('lng').value;
        const radius = document.getElementById('radius').value;
        
        if (lat && lng) {
          params.append('lat', lat);
          params.append('lng', lng);
          params.append('radius', radius || '50');
        }
        
        // Try using "vendors" (plural) as the parameter name for vendor filters
        document.querySelectorAll('input[name="vendor"]:checked').forEach(function(checkbox) {
          params.append('vendor', checkbox.value);  // Change 'vendor' to 'vendors'
        });
        
        // The rest of your code is correct
        document.querySelectorAll('input[name="status"]:checked').forEach(function(checkbox) {
          params.append('status', checkbox.value);
        });
        
        document.querySelectorAll('input[name="location"]:checked').forEach(function(checkbox) {
          params.append('location', checkbox.value);
        });
        
        document.querySelectorAll('input[name="location_type"]:checked').forEach(function(checkbox) {
          params.append('location_type', checkbox.value);
        });
        
        document.querySelectorAll('input[name="transporttype"]:checked').forEach(function(checkbox) {
          params.append('transporttype', checkbox.value);
        });
        
        // Always include these fields
        // params.append('include_fields', 'status');
        // params.append('include_fields', 'location_type');
        
        loadMapData(params.toString());
      });
  
      // Reset filters button
      document.getElementById('reset-filters').addEventListener('click', function() {
        document.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
          checkbox.checked = false;
        });
        
        document.getElementById('lat').value = '';
        document.getElementById('lng').value = '';
        document.getElementById('radius').value = '50';
        
        remove_pin();
        // loadMapData('include_fields=status&include_fields=location_type');
        loadMapData();
      });
  
      // Use current location checkbox
      document.getElementById('useCurrentLocation').addEventListener('change', function() {
        if (this.checked) {
          if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
              function(position) {
                document.getElementById('lat').value = position.coords.latitude.toFixed(6);
                document.getElementById('lng').value = position.coords.longitude.toFixed(6);
                const rad = parseFloat(document.getElementById('radius').value) || 50;
                update_pos_point_to_map(position.coords.latitude, position.coords.longitude, rad);
              }, 
              function(error) {
                console.error("Error getting location:", error);
                alert("Could not get your location. Please enter coordinates manually.");
                document.getElementById('useCurrentLocation').checked = false;
              }
            );
          } else {
            alert("Geolocation is not supported by this browser. Please enter coordinates manually.");
            this.checked = false;
          }
        }
      });
  
      // Coordinate input handlers
      document.getElementById('lat').addEventListener('input', updateFromCoordinateInputs);
      document.getElementById('lng').addEventListener('input', updateFromCoordinateInputs);
      document.getElementById('radius').addEventListener('input', function() {
        const lat = parseFloat(document.getElementById('lat').value);
        const lng = parseFloat(document.getElementById('lng').value);
        const radiusKm = parseFloat(this.value) || 50;
        
        if (!isNaN(lat) && !isNaN(lng) && radiusMarker) {
          update_radius_circle(lat, lng, radiusKm);
        }
      });
  
      // Handle window resize
      window.addEventListener('resize', function() {
        map.invalidateSize();
      });
  
      // Initialize map properly after DOM is fully loaded
      // setTimeout(function() {
      //   console.log("Map initialized after DOM load");
      //   map.invalidateSize();
      // }, 100);
      // map.invalidateSize();
      setTimeout(function() {
        if (map){
          map.invalidateSize();
        }        
      }, 300);
    }

    // Set up sidebar toggle functionality
    function setupSidebarToggle() {
      const toggleSidebarBtn = document.getElementById('toggle-sidebar');
      const sidebarRight = document.querySelector('.sidebar-right');
      
      if (!toggleSidebarBtn || !sidebarRight) return;
      
      toggleSidebarBtn.addEventListener('click', function() {
        sidebarRight.classList.toggle('collapsed');
        
        // Store preference in localStorage
        localStorage.setItem('connections_list_collapsed', sidebarRight.classList.contains('collapsed'));
        
        // Resize map to adjust to new layout
        setTimeout(function() {
          if (map) map.invalidateSize();
        }, 300); // Wait for transition to complete
      });
      
      // Check if sidebar was collapsed in previous session
      const wasCollapsed = localStorage.getItem('connections_list_collapsed');
      if (wasCollapsed === 'true') {
        sidebarRight.classList.add('collapsed');
        // Resize map after sidebar is collapsed
        setTimeout(function() {
          if (map) map.invalidateSize();
        }, 100);
      }
    }

    // Set up sidebar toggle
    setupSidebarToggle();

    // If URL has params on initial load, use them for the navigation links
    const initialParams = getURLParameters();
    if (initialParams) {
      last_used_params = initialParams;
      updateNavigationLinks();
    }
  });