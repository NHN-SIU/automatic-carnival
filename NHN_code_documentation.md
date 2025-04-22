# Documentation – Intern Project from UiT, Spring 2025

## 1. Overview
(table of content)?



## 2. Getting started
The getting started section is inspired by nautobots [nautobot-docker-compose](https://github.com/nautobot/nautobot-docker-compose) documentation

### 2.0 What do you need to install on you local computer?
#### 2.0.0 Install docker
Install docker and make sure it runs.
#### 2.0.1 Install poetry
It is recommended installing poetry by following [one of the installation methods detailed in their documentation](https://python-poetry.org/docs/#installing-with-pipx)

### 2.1 Clone repository
Navigate to a repository and clone this project:
`git clone https://github.com/NHN-SIU/automatic-carnival.git`

### 2.2 Change creds.env, development.env 
The app reades cread.env and development.env. development.env already exists. Copy the example creds file and modify it if you want:
'cp development/creds.example.env development/creds.env'


### 2.3 Activate environment and install dependencies
Create the poetry virtual environment
'poetry shell'

'poetry lock'

'poetry install'

The last command, 'poetry install', will install all of the project dependencies for you to manage your Nautobot project. 
This includes installing the invoke Python project.

### 2.4 Build and start
You can build and start the application with the following steps
'invoke build'
'invoke start'

Populate the app with test data:
'python test_data/import_data.py'

### 2.5 Clean up everything and start from scratch
'invoke destroy'
'invoke build'
'invoke start'


## Features

### List feature

### Map Feature

### Graph feature

##  Known Issues / Limitations

## Future Work / TODO
