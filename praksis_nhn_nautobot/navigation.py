"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:praksis_nhn_nautobot:samband_list",
        name="Praksis NHN Nautobot",
        permissions=["praksis_nhn_nautobot.view_samband"],
        buttons=(
            NavMenuAddButton(
                link="plugins:praksis_nhn_nautobot:samband_add",
                permissions=["praksis_nhn_nautobot.add_samband"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Apps",
        groups=(NavMenuGroup(name="Praksis NHN Nautobot", items=tuple(items)),),
    ),
)
