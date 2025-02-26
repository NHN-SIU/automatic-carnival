# Running the Program
This manual is inspired by the official Nautobot Docker Compose repository, upon which this project is built.

## Prerequisites
- **Poetry**: Ensure that Poetry is installed on your local machine.
- **Docker**: Install Docker to manage containerized applications.

## Setting Up the Virtual Environment
To run the program, create a virtual environment using Poetry:

    poetry shell
    poetry lock
    poetry install --no-root

Note: The invoke tool is included during the poetry install process; no separate installation is required.

## Building and Starting Nautobot
Use the following commands to build and start Nautobot:

    invoke build
    invoke start

Alternatively, to view container logs in real-time:

    invoke debug

**Note**: Exiting debug mode will stop all running containers.
**Note**: You may have to wait a bit for the container to connect to the port

## Resetting the Environment
To clean up and start fresh:

    invoke destroy
    invoke build
    invoke db-import
    invoke start
*Note*: The invoke db-import command requires a pre-existing database backup. (Not necessary)

## Exporting the Current Database
To export the current database state:

    invoke db-export

## CLI Helper Commands
The project comes with a CLI helper based on invoke to help manage the Nautobot environment. The commands are listed below in 2 categories environment and utility.

Each command can be executed with a simple invoke . Each command also has its own help invoke  --help.
### Manage Nautobot environment

  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
  db-export        Export Database data to nautobot_backup.dump.
  db-import        Import test data.

### Utility
  cli              Launch a bash shell inside the running Nautobot container.
  migrate          Run database migrations in Django.
  nbshell          Launch a nbshell session.
