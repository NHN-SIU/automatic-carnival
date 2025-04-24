document.addEventListener('DOMContentLoaded', function() {
    let map = null;
    
    // Status colors
    const statusColors = {
      'Active': '#4CAF50',     // Green
      'Planned': '#FFC107',    // Yellow/Amber
      'Decommissioned': '#F44336', // Red
      'Planning': '#FFC107',   // Yellow
      'Unknown': '#9E9E9E'     // Grey (fallback)
    };
    
    // Status Bootstrap classes
    const statusClasses = {
      'Active': 'bg-success',
      'Planned': 'bg-warning',
      'Decommissioned': 'bg-danger',
      'Planning': 'bg-warning',
      'Unknown': 'bg-secondary'
    };
    
    // Location type icon mapping - using only the most relevant types
    const locationTypeIcons = {
      'Hospital': {
        icon: 'fa-solid fa-hospital',
        color: '#E91E63'
      },
      'Datacenter': {
        icon: 'fa-solid fa-server',
        color: '#673AB7'
      },
      'Data Center': {
        icon: 'fa-solid fa-server',
        color: '#673AB7'
      },
      'Pharmacy': {
        icon: 'fa-solid fa-prescription-bottle-medical',
        color: '#009688'
      },
      'Primary Care': {
        icon: 'fa-solid fa-user-doctor',
        color: '#FF5722'
      },
      'Medical Imaging': {
        icon: 'fa-solid fa-x-ray',
        color: '#8BC34A'
      }
    };
    
    // Fixed endpoint colors - always make points distinct
    const POINT_A_COLOR = '#3498db'; // Blue
    const POINT_B_COLOR = '#e74c3c'; // Red
    
    // Initialize map
    function initMap() {
      map = L.map('connection-map');
      
      // Add base map layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);
      
      return map;
    }
    
    // Helper function to get icon for location type
    function getLocationIcon(locationType, isPointA) {
      // Get icon based on location type
      const config = locationTypeIcons[locationType] || {
        icon: 'fa-solid fa-location-dot',
        color: '#3186cc'
      };
      
      // Override the color to ensure points A and B are always visually distinct
      // Even if they have the same location type
      const iconColor = isPointA ? POINT_A_COLOR : POINT_B_COLOR;
      
      return L.divIcon({
        html: `<div style="background-color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.3); border: 2px solid ${iconColor};">
                <i class="${config.icon}" style="color: ${iconColor}; font-size: 16px;"></i>
              </div>`,
        className: '',
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -14]
      });
    }
    
    // Render icon for a location in the sidebar
    function renderLocationIcon(elementId, category, isPointA) {
      const config = locationTypeIcons[category] || {
        icon: 'fa-solid fa-location-dot',
        color: '#3186cc'
      };
      
      // Use consistent colors for points A and B
      const iconColor = isPointA ? POINT_A_COLOR : POINT_B_COLOR;
      
      document.getElementById(elementId).innerHTML = `<i class="${config.icon}" style="color: ${iconColor}; font-size: 14px;"></i>`;
    }
    
    // Render map for the connection
    function renderConnectionMap(data) {
      // Initialize map if not already done
      if (!map) map = initMap();
      
      const bounds = [];
      const statusColor = statusColors[data.status] || statusColors.Unknown;
      
      // Use the coordinates directly from our simplified API response
      const pointACoords = data.pop_a_coords;
      const pointBCoords = data.pop_b_coords;
      
      // Add markers and line if coordinates are valid
      if (pointACoords) {
        L.marker(pointACoords, {
          icon: getLocationIcon(data.pop_a_category, true) // true = point A
        }).bindPopup(`
          <div style="min-width: 200px;">
            <strong>${data.name} - Point A</strong><br>
            ${data.pop_a_address ? `<strong>Address:</strong> ${data.pop_a_address}<br>` : ''}
            ${data.pop_a_category ? `<strong>Category:</strong> ${data.pop_a_category}<br>` : ''}
            ${data.pop_a_room ? `<strong>Room:</strong> ${data.pop_a_room}` : ''}
          </div>
        `).addTo(map);
        
        bounds.push(pointACoords);
      }
      
      if (pointBCoords) {
        L.marker(pointBCoords, {
          icon: getLocationIcon(data.pop_b_category, false) // false = point B
        }).bindPopup(`
          <div style="min-width: 200px;">
            <strong>${data.name} - Point B</strong><br>
            ${data.pop_b_address ? `<strong>Address:</strong> ${data.pop_b_address}<br>` : ''}
            ${data.pop_b_category ? `<strong>Category:</strong> ${data.pop_b_category}<br>` : ''}
            ${data.pop_b_room ? `<strong>Room:</strong> ${data.pop_b_room}` : ''}
          </div>
        `).addTo(map);
        
        bounds.push(pointBCoords);
      }
      
      if (pointACoords && pointBCoords) {
        L.polyline([pointACoords, pointBCoords], {
          color: statusColor,
          weight: 4,
          opacity: 0.8,
          smoothFactor: 1
        }).bindPopup(`
          <div style="min-width: 200px;">
            <strong>${data.name}</strong><br>
            <strong>Status:</strong> ${data.status || 'Unknown'}<br>
            <strong>Vendor:</strong> ${data.vendor || 'Not specified'}<br>
            <strong>Type:</strong> ${data.type_name || 'Not specified'}
          </div>
        `).addTo(map);
      }
      
      // Set map view
      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [30, 30] });
      } else {
        map.setView([65.4, 17.0], 5);
        
        // Show message if no valid coordinates
        L.marker([65.4, 17.0])
          .bindPopup("No valid coordinates available for this connection")
          .addTo(map)
          .openPopup();
      }
    }
    
    // Populate details for a connection point
    function populatePointDetails(elementId, data, isPointA) {
      const address = isPointA ? data.pop_a_address : data.pop_b_address;
      const category = isPointA ? data.pop_a_category : data.pop_b_category;
      const room = isPointA ? data.pop_a_room : data.pop_b_room;
      const coords = isPointA ? data.pop_a_coords : data.pop_b_coords;
      
      // Add color indicator class to show which point is which
      const detailsEl = document.getElementById(elementId);
      detailsEl.classList.add(isPointA ? 'point-a-color' : 'point-b-color');
      
      let html = '';
      
      if (address) {
        html += `<p><strong>Address:</strong> ${address}</p>`;
      }
      
      if (category) {
        html += `<p><strong>Category:</strong> ${category}</p>`;
      }
      
      if (room) {
        html += `<p><strong>Room:</strong> ${room}</p>`;
      }
      
      if (coords) {
        html += `<p><strong>Coordinates:</strong> ${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}</p>`;
      }
      
      if (!html) {
        html = '<p class="text-muted">No details available</p>';
      }
      
      detailsEl.innerHTML = html;
    }
    
    // Update page with connection data
    function updatePageWithConnectionData(data) {
      console.log('Connection data:', data);
      
      // Check if we got valid data
      if (!data || !data.name) {
        throw new Error('Invalid or empty connection data');
      }
      
      // Update page title and header
      document.title = `${data.name} - Connection Details`;
      document.getElementById('connection-name').textContent = data.name;
      
      // Update badges
      let badgesHtml = '';
      
      // Status badge
      const statusClass = statusClasses[data.status] || statusClasses.Unknown;
      badgesHtml += `<span class="badge ${statusClass} me-2">${data.status || 'Unknown'}</span>`;
      
      // Reference badge
      if (data.reference) {
        badgesHtml += `<span class="badge bg-light text-dark me-2">Ref: ${data.reference}</span>`;
      }
      
      // Bandwidth badge
      if (data.bandwidth) {
        badgesHtml += `<span class="badge bg-info me-2">${data.bandwidth}</span>`;
      }
      
      document.getElementById('connection-badges').innerHTML = badgesHtml;
      
      // Update quick info cards
      document.getElementById('vendor-info').textContent = data.vendor || 'Not specified';
      document.getElementById('type-info').textContent = data.type_name || 'Not specified';
      document.getElementById('location-info').textContent = data.location || 'Not specified';
      document.getElementById('transport-info').textContent = data.transport_type || 'Not specified';
      
      // Update detail link
      document.getElementById('details-link').href = `/plugins/praksis-nhn-nautobot/samband/${connectionId}/`;
      
      // Update graph link if it exists in the template but wasn't set by Django
      const graphLink = document.getElementById('graph-link');
      if (graphLink && graphLink.classList.contains('disabled')) {
        graphLink.href = `/plugins/praksis-nhn-nautobot/samband/graph/${connectionId}/`;
        graphLink.classList.remove('disabled');
      }
      
      // Update endpoint icons with the specific category for each point with distinct colors
      renderLocationIcon('point-a-icon', data.pop_a_category, true); // true = point A
      renderLocationIcon('point-b-icon', data.pop_b_category, false); // false = point B
      
      // Update endpoint details
      populatePointDetails('point-a-details', data, true);
      populatePointDetails('point-b-details', data, false);
      
      return data;
    }
    
    // Main execution - only proceed if we have a connection ID
    if (connectionId) {
      // Fetch connection data and update page
      fetch(`/plugins/praksis-nhn-nautobot/api/samband/map-data/?connection_id=${connectionId}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Connection not found (Status: ${response.status})`);
          }
          return response.json();
        })
        .then(data => {
          console.log('Raw data from API:', data);
          
          // Provide informative error if data structure is missing expected fields
          if (!data) {
            throw new Error('No data returned from API');
          }
          
          // Check for required coordinates
          if (!data.pop_a_coords && !data.pop_b_coords) {
            console.warn('No valid coordinates found for this connection');
          }
          
          updatePageWithConnectionData(data);
          
          // Use the simplified API response for map rendering
          renderConnectionMap(data);
        })
        .catch(error => showError(error));
    } else {
      showError(new Error('No connection ID provided'));
    }
  });