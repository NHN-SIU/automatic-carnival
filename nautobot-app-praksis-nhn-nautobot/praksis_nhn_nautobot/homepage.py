"""Homepage configuration for praksis_nhn_nautobot plugin."""

from nautobot.core.apps import HomePageItem, HomePagePanel
from praksis_nhn_nautobot import models

def get_connection_data(request):
    """Get connection data for homepage display."""
    return models.NHNModel.objects.all()



layout = (
    HomePagePanel(
        name="Network Connections",
        weight=10,
        items=(
            HomePageItem(
                name="NHN Connections",
                model=models.NHNModel,
                weight=100,
                link="plugins:praksis_nhn_nautobot:nhnmodel_list",
                description="Manage Norwegian Health Network connections.",
                permissions=["praksis_nhn_nautobot.view_nhnmodel"],
            ),
        ),
    ),
    # Use only compatible parameters for the second panel
    HomePagePanel(
        name="Connection Statistics",
        weight=20,
        items=(
            HomePageItem(
                name="Connection Management",
                link="plugins:praksis_nhn_nautobot:nhnmodel_list",
                weight=100,
                description=f"Manage your network connections.",
                permissions=["praksis_nhn_nautobot.view_nhnmodel"],
            ),
            HomePageItem(
                name="Graph View",
                link="plugins:praksis_nhn_nautobot:nhnmodel_list", # You can replace with graph view URL if applicable
                weight=200,
                description="Visualize connection hierarchy.",
                permissions=["praksis_nhn_nautobot.view_nhnmodel"],
            ),
        ),
    ),
)