from django.urls import resolve
from nautobot.core.apps import HomePagePanel, HomePageItem
from praksis_nhn_nautobot import models

class CustomHomepageMiddleware:
    """Middleware to customize the Nautobot homepage."""
    
    def __init__(self, get_response):
        print("middleware initialized")
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        print(f"Middleware called for path {request.path}")
        
        # Only modify the homepage for authenticated users
        if request.path == '/' and hasattr(request, 'user') and request.user.is_authenticated:
            print(f"Processing homepage for user {request.user.username}")

            attr = [attr for attr in dir(request) if not attr.startswith('_')]

            for att in attr:
                print(f"{att}: {getattr(request, att)}")

            if hasattr(request, 'resolver_match'):
                print(f"Resolver_match: {request.resolver_match}")
                print(f"View name: {request.resolver_match.view_name}")
                print(f"View func: {request.resolver_match.func.__name__}")

            # Replace the panels in the view context
            if hasattr(request, "context_type"):
                print("Response context keys:", list(response.context_type.keys()))

                # Create our custom panels
                custom_panels = [
                    HomePagePanel(
                        name="NHN Connections",
                        weight=10,  # Very low weight to appear at top
                        items=(
                            HomePageItem(
                                name="All Connections",
                                model=models.NHNModel,
                                weight=100,
                                link="plugins:praksis_nhn_nautobot:nhnmodel_list",
                                description="Manage Norwegian Health Network connections.",
                                permissions=("praksis_nhn_nautobot.view_nhnmodel",),
                            ),
                        ),
                    ),
                    HomePagePanel(
                        name="Connection Analytics",
                        weight=20,
                        items=(
                            HomePageItem(
                                name="Connection Statistics",
                                weight=100,
                                link="plugins:praksis_nhn_nautobot:nhnmodel_list", 
                                description=f"Currently {models.NHNModel.objects.count()} connections in database.",
                                permissions=("praksis_nhn_nautobot.view_nhnmodel",),
                            ),
                            HomePageItem(
                                name="Connection Graph",
                                link="plugins:praksis_nhn_nautobot:nhnmodel_list",
                                weight=200,
                                description="View hierarchy relationships.",
                                permissions=("praksis_nhn_nautobot.view_nhnmodel",),
                            ),
                        ),
                    ),
                ]
                
                # Get only the panels we want to keep from the original list
                # For example, keep only the User panel
                user_panels = [p for p in request._homepage_panels if p.name == "User"]
                
                # Replace the panels with our custom ones, plus any panels we want to keep
                request._homepage_panels = custom_panels + user_panels
        
        return response