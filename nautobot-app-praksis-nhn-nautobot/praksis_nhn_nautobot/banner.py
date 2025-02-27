from django.utils.html import format_html

from nautobot.apps.ui import Banner, BannerClassChoices

def banner(context, *args, **kwargs):
    """Greet the user, if logged in."""
    # Request parameters can be accessed via context.request
    if not context.request.user.is_authenticated:
        # No banner if the user isn't logged in
        return None
    else:
        return Banner(
            content=format_html("Hello, <strong>{}</strong>! 👋", context.request.user),
            banner_class=BannerClassChoices.CLASS_SUCCESS,
        )