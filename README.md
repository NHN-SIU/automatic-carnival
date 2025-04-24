# Documentation – Intern Project from UiT, Spring 2025

## 1. Overview

(table of content)?



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

## Features

### List feature

### Map Feature

### Graph feature

##  Known Issues / Limitations

## Future Work / TODO
