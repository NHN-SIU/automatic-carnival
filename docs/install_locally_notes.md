

# These are the required dependencies to run nautobot:
## Dependencies    -- Role         -- Min. version
Python          -- Application  -- 3.9
MySQL           -- Database     -- 12.0
PostGreSQL      -- Database     -- 8.0
Redis           -- Cache, Queue -- 4.0
Git             -- Additional   -- 2.0


# Reccomended dependencies for production deployment:
- uWSGI WSGI server
- NGINX HTTP server
- External authentication service for SSO such as SAML, OAuth2, or LDAP, or an authenticating proxy

# For additional features:
- NAPALM support for retrieving operational data from network devices
- Prometheus metrics for exporting application performance and telemetry data


# Add nautobot system user:
sudo useradd --system --shell /bin/bash --create-home --home-dir ...mydir/opt/nautobot nautobot

To switch to the nautobot user use
sudo su - nautobot
This will give you access to the directory

Steps:
- Create Virtual environment
- Switch to nautobot
- Prepare Virtual Environment
- Install Nautobot
- Make Configurations:
    - ALLOWED_HOSTS: ["*"]   === Set for a quickstart but not suitable for production
    - DATABASES = {
        "default": {
            "NAME": os.getenv("NAUTOBOT_DB_NAME", "nautobot"),  # Database name
            "USER": os.getenv("NAUTOBOT_DB_USER", ""),  # Database username
            "PASSWORD": os.getenv("NAUTOBOT_DB_PASSWORD", ""),  # Database password
            "HOST": os.getenv("NAUTOBOT_DB_HOST", "localhost"),  # Database server
            "PORT": os.getenv("NAUTOBOT_DB_PORT", "3306"),  # Database port (leave blank for default)
            "CONN_MAX_AGE": int(os.getenv("NAUTOBOT_DB_TIMEOUT", "300")),  # Database timeout
            "ENGINE": "django.db.backends.mysql",  # Database driver ("mysql")
            "OPTIONS": {
                    "charset": "utf8mb4" # Enable full Unicode support
            {
        {
    }
    - env added: (inside ~/.bashrc -- can be accessed via echo $ENVIRONMENT_VARIABLE)
        - NAUTOBOT_DB_NAME: nautobot
        - NAUTOBOT_DB_USER: nautobot
        - NAUTOBOT_DB_PASSWORD: norskhelsenett123456789_!
        - NAUTOBOT_DB_HOST: localhost
        - NAUTOBOT_DB_PORT: 3306 
        - NAUTOBOT_DB_TIMEOUT: not set
- Prepare the Database          --"nautobot-server migrate"
- Create SuperUser              --"nautobot-server createsuperuser"
- Create Static Directories     --"nautobot-server collectstatic"
    - Nautobot relies upon many static files including:
        - git - For storing Git repositories
        - jobs - For storing custom Jobs
        - media - For storing uploaded images and attachments (such as device type images)
        - static - The home for CSS, JavaScript, and images used to serve the web interface
    - Each of these have their own corresponding setting that defined in nautobot_config.py, but by default they will all be placed in NAUTOBOT_ROOT unless you tell Nautobot otherwise by customizing their unique variable
    - The collectstatic command will create these directories if they do not exist, and in the case of the static files directory, it will also copy the appropriate files:


