![header](docs/header.png)

# Documentation – Intern Project from UiT, Spring 2025

## 1. Overview

(table of content)?

## 2. Getting started

> This setup is inspired by [nautobot-docker-compose](https://github.com/nautobot/nautobot-docker-compose).

For more detailed instructions on setting up your development environment, see [dev_environment.md](docs/dev_environment.md).

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

## Features

### List feature

### Map Feature

The map is built with **[Leaflet](https://leafletjs.com/)**, a client-side JavaScript library for interactive maps. Leaflet handles map interaction (e.g., panning, zooming, placing markers), but requires an external **tilemap** source for the actual map visuals.

This project uses **[OpenStreetMap](https://wiki.openstreetmap.org/)** as the tile provider. OpenStreetMap is free and open-source. An internet connection is required to fetch tiles, but tiles can be downloaded for offline use, it is crazy large: https://wiki.openstreetmap.org/wiki/Downloading_data

1. Filters are fetched from the server.
2. Filtered point data is requested via API. So the site would work fine as long as it gets the right data via API
3. Leaflet plots points on the map using markers.
4. **Font Awesome** is used for marker icons.

Notes:

- **Folium** was tested but not used due to server-side rendering. Leaflet was chosen for full client-side control and better performance.


### Graph feature

Refer to [graph.md](docs/graph.md).

## Known Issues / Limitations

## Future Work / TODO
