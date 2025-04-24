"""Menu items."""

from nautobot.apps.ui import NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:praksis_nhn_nautobot:samband_list",
        name="Table View",
        permissions=["praksis_nhn_nautobot.view_samband"],
    ),
    NavMenuItem(
        link="plugins:praksis_nhn_nautobot:samband_client_map",
        name="Map View",
        permissions=["praksis_nhn_nautobot.view_samband"],
    ),
    NavMenuItem(
        link="plugins:praksis_nhn_nautobot:samband_graph",
        name="Graph View",
        permissions=["praksis_nhn_nautobot.view_samband"],
    ),
)

menu_items = (
    NavMenuTab(
        name="Apps",
        groups=(NavMenuGroup(name="Praksis NHN Nautobot", items=tuple(items)),),
    ),
)
