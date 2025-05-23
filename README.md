# Documentation – Intern Project from UiT, Spring 2025

**Interns:**
    Gard Schive             - Map
    Lars Moen Storvik       - List
    Marius Solaas           - Graph

## 1. Overview

### Project Structure

Below is an overview of the key files and their purposes:  

├─── development/  
│    ├─── app_config_schema.py:         Defines the schema for application configuration.  
│    ├─── creds.env:                    Stores sensitive environment variables like API keys and database credentials.  
│    ├─── development.env:              Contains environment-specific settings for development purposes.  
│    ├─── docker-compose.base.yml:      Base configuration for Docker Compose.  
│    ├─── docker-compose.dev.yml:       Docker Compose configuration for development.  
│    ├─── docker-compose.mysql.yml:     Docker Compose configuration for MySQL database.  
│    ├─── docker-compose.postgres.yml:  Docker Compose configuration for PostgreSQL database.   
│    ├─── docker-compose.redis.yml:     Docker Compose configuration for Redis.  
│    ├─── Dockerfile:                   Defines the Docker image used to containerize the application.  
│    └─── nautobot_config.py:           Configuration file for Nautobot.  
|  
├─── praksis_nhn_nautobot/              Main Django app for managing NHN-related logic and interfaces.  
│    ├─── api/  
|    |    ├─── serializers.py:          Defines how data is serialized/deserialized for API input/output.  
|    |    ├─── urls.py:                 Maps API URL endpoints to view functions or classes.  
|    |    └─── views.py:                Handles the logic for processing API requests and returning responses.  
│    ├─── migrations/:                  Contains database migration files.  
│    ├─── services/:                    Contains service layer logic for the application.  
│    ├─── static/:                      Directory for static files like CSS, JavaScript, and images.  
│    ├─── templates/  
|    |    └─── praksis_nhn_nautobot/:   Directory for HTML templates.    
│    ├─── tests/:                       Contains unit and integration tests for the project.    
│    ├─── filters.py:                   Defines filters for querying data.  
│    ├─── forms.py:                     Contains form definitions for user input.  
│    ├─── models.py:                    Defines the database models for the application.  
│    ├─── navigation.py:                Handles navigation-related logic.  
│    ├─── tables.py:                    Defines table structures for displaying data.  
│    ├─── urls.py:                      Maps URL patterns to views.  
│    └─── views.py:                     Contains view logic for rendering templates and handling requests.  
|  
├─── test_data/:                 Directory containing sample data for testing and populating the application.  
├─── tasks.py:                   Defines custom tasks for the project.  
├─── README.md:                  Documentation file for the project.  

## 2. Getting started

> This setup is inspired by [nautobot-docker-compose](https://github.com/nautobot/nautobot-docker-compose).

### 2.1 Prerequisites

Ensure you have the following installed on your local machine:

#### 2.1.1 Docker

Install [Docker](https://docs.docker.com/get-docker/) and verify that it is running on your system.

#### 2.1.2 Poetry

We recommend installing Poetry using one of the official methods:  
👉 [Poetry Installation Guide](https://python-poetry.org/docs/#installing-with-pipx)

---

### 2.2 Clone the repository

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/NHN-SIU/automatic-carnival.git
cd automatic-carnival
```

### 2.3 Change creds.env, development.env

The application reads settings from creds.env and development.env.

- development.env already exists.
- Copy the example credentials file and customize it if needed:

```bash
cp development/creds.example.env development/creds.env
```

### 2.4 Activate Environment and Install Dependencies

Set up the virtual environment and install all dependencies:

```bash
poetry shell
poetry lock
poetry install
```

> The 'poetry install' command will set up the necessary Python packages, including the invoke CLI tool used to manage this Nautobot project.

### 2.5 Build and Start the Application

Build and start the application using the following commands:

```bash
invoke build
invoke start
```

⚠️ It may take some time for the application to start up.

Once running, you can log inn with

- **username**: 'admin'
- **password**: 'admin'

To populate the app with test data from the test_data/ directory:
Populate the app with test data in the test_data diectory:

```bash
python3 import_data.py
```

### 2.6 Clean up everything and start from scratch

To clean up and start fresh:

```bash
invoke destroy
invoke build
invoke start
```

### 2.7 Testing

To invoke the tests in 'praksis_nhn_nautobot/tests/' run this command:

```bash
invoke tests
```

By default, this command runs several checks, including ruff, yamllint, poetry, and others, in addition to the unit tests.  
If you want to run **only the unit tests**, it is recommended to temporarily comment out the other checks in tasks.py (around line 860) before executing the command.  

## Features

### List feature

The list view provides a textual representation of `samband` entries, including selected data fields.

Key functionalities:

1. Display a list of samband with relevant metadata.
1. Filtering functionality based on a single field value at a time.
1. Switch to map or graph with the specific samband filtered upon.

**Note:** Unlike the map view, the list does not currently support filtering by multiple values in the same field (e.g., showing samband in both **"Bergen"** and **"Oslo"** at the same time).

### Single samband fetaure
This feature can be used by clicking a specific samband in the samband list
1. View information of a specific samband
1. Direct links to switch to map or graph view for a specific samband.
1. Advanced settings
1. Notes
1. Change Log

### Map Feature

´
The map is built with **[Leaflet](https://leafletjs.com/)**, a client-side JavaScript library for interactive maps. Leaflet handles map interaction (e.g., panning, zooming, placing markers), but requires an external **tilemap** source for the actual map visuals.

This project uses **[OpenStreetMap](https://wiki.openstreetmap.org/)** as the tile provider. OpenStreetMap is free and open-source. An internet connection is required to fetch tiles, but tiles can be downloaded for offline use, it is crazy large: https://wiki.openstreetmap.org/wiki/Downloading_data

1. Filters are fetched from the server.
2. Filtered point data is requested via API. So the site would work fine as long as it gets the right data via API
3. Leaflet plots points on the map using markers.
4. **Font Awesome** is used for marker icons.

Notes:

**Folium** was tested but not used due to server-side rendering. Leaflet was chosen for full client-side control and better performance.


### Graph feature

The graph data is build using **[NetworkX](https://networkx.org/documentation/stable/)**, a Python package for creation of complex networks. NetworkX handles the backend formatting of the objects in node/egde format.

Then the graph is rendered on the frontend using **[Vis.js](https://visjs.org/)**, a client-side Javascript library which can easily handle large amount of data. Vis.js has its own component for rendering a Network, which makes it easy to organize the layout and physics of the nodes. It also supports hierarchical layout, which is used for the view of an individual node (Samband).

For more details (Norwegian), refer to [graph.md](docs/graph.md).

## Known Issues / Limitations
Searching in the list and then going to the map will not work. the url will add "q="..."", this is not supported by the api. Only the filters that are listed in map view is supported.

Use my location button does not work, gives seemingly random locations

- The filtering in the individual graph view to table/map does not work, because the graph view implements a custom fetching function for the hierarchy for a given node. Now, the filters in table and map view gets passed on as URL-params to the other views. We have seen on the possibility to store the instances currently in the view in cache to pass them on to the different views, but have not comed to a definitive solution.

### Limitations of list feature

- The list view only supports filtering by **one field value at a time**.
  - For example, it is **not possible** to filter for `samband` located in **both "Bergen" and "Oslo"** simultaneously.
  - In contrast, the **map view** supports multi-value filtering.
- Upon filtering through "search bar", switching to map or graph doesn't work
 - Samband filters is passed through the url, but the "search" filter is not compatible with the current map/graph implementatio

### Graph feature

- The spacing of nodes are decided by the physics module, and it based on the radius of the node. This means that the label/text underneath is not a part of the spacing, which may lead to overlapping text between nodes, espescially when many labels are enabled.
- The "graph view" button in the sidebar fetches all the Samband instances. This means that for a very large number of instances, the layout may become cluttered and slow.
- In the individual graph view, the backend fetches the relations for a node for a given depth. It may have been benefitial to allow toggling for further hierarchy when a node is clicked.

## Future Work / TODO
Show the graph/hierarchy on the map.
- Create a unified filter system that works across all views.

### Graph view

- Small bug: in individual graph view, when you hover over the main node in orange, it changes color to the dark blue that would otherwise be applied to the other nodes. It should still be in the orange color.
- It would be cool to add search capability to locate and highlight specific nodes in the graph
- Implement path-finding to show connections between node X and Y
