"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:praksis_nhn_nautobot:dashboard",
        name="Dashboard",
        permissions=["praksis_nhn_nautobot.view_nhnmodel"],
    ),
    NavMenuItem(
        link="plugins:praksis_nhn_nautobot:nhnmodel_list",
        name="Se samband",
        permissions=["praksis_nhn_nautobot.view_nhnmodel"],
        buttons=(
            NavMenuAddButton(
                link="plugins:praksis_nhn_nautobot:nhnmodel_add",
                permissions=["praksis_nhn_nautobot.add_nhnmodel"],
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
