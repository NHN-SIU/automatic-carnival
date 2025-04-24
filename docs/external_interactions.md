# External Interactions

This document describes external dependencies and prerequisites for this App to operate, including system requirements, API endpoints, interconnection or integrations to other applications or services, and similar topics.

## External System Integrations

### From the App to Other Systems

- **Nautobot Core:**  
  The app relies on Nautobot as its core platform. All data models and API endpoints are built on top of Nautobot's plugin framework.
- **NetworkX (Python):**  
  Used for backend graph data processing and serialization.
- **Vis.js (JavaScript):**  
  Used in the frontend for interactive graph/network visualization.
- **Leaflet.js (JavaScript):**  
  Used for map-based visualizations of connections.

### From Other Systems to the App

- **API Consumers:**  
  External systems or scripts can interact with the app via the provided REST API endpoints (see below).
- **Authentication:**  
  API access requires valid Nautobot authentication (token or session-based).

## Nautobot REST API endpoints

The app exposes several REST API endpoints for integration and data retrieval.

### Example: Get Map Data for Connections

**Endpoint:**  
`GET /plugins/praksis-nhn-nautobot/api/samband/map-data/`

**Parameters:**

- `connection_id` (optional): Filter by specific connection.
- `status`, `vendor`, `location`, `location_type` (optional): Filter results.

**Python Example:**

```python
import requests

url = "https://<your-nautobot-host>/plugins/praksis-nhn-nautobot/api/samband/map-data/"
params = {"status": "Active"}
headers = {"Authorization": "Token <your-api-token>"}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```

## System Requirements

- Nautobot >= 2.0.0
- Python >= 3.10
- NetworkX (Python package)
- Vis.js and Leaflet.js (included via static files or CDN)
