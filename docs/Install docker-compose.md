# Installation Log for Nautobot Docker Compose

This file documents the changes made when installing the Nautobot Docker Compose repository. The goal is to make the process reproducible for future setups.

## Steps Followed
I followed the **"Getting Started"** tutorial from the repository, with the following modifications:

1. Cloned the repository and copied it into the src/ folder, removing the Git history to detach it from the original repository.
2. Used MySQL instead of PostgreSQL:
    - Instead of copying 'invoke.example.yml' (as described in step 7), I copied 'invoke.mysql.yml' to 'invoke.yml'.
    - This ensures that MySQL is used as the database instead of PostgreSQL.
These modifications adapt the installation to fit the project’s needs.

In poetry.lock I added "package-mode = false". Poetry couldn't install dependencies without it, probably because I changed the directory name from nautobot-docker.compose to src