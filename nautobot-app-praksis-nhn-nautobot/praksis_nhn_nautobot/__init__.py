"""App declaration for praksis_nhn_nautobot."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class PraksisNhnNautobotConfig(NautobotAppConfig):
    """App configuration for the praksis_nhn_nautobot app."""

    name = "praksis_nhn_nautobot"
    verbose_name = "Praksis NHN Nautobot"
    version = __version__
    author = "Marius Solaas, Lars M. Storvik, Gard Schive"
    description = "Nautobot application for NHN by Praksis student spring 2025."
    base_url = "praksis-nhn-nautobot"
    required_settings = []
    min_version = "2.0.0"
    max_version = "2.9999"
    default_settings = {}
    caching_config = {}
    docs_view_name = "plugins:praksis_nhn_nautobot:docs"

config = PraksisNhnNautobotConfig  # pylint:disable=invalid-name
