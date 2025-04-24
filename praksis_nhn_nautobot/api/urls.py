"""Django API urlpatterns declaration for praksis_nhn_nautobot app."""

from nautobot.apps.api import OrderedDefaultRouter
from django.urls import path

from praksis_nhn_nautobot.api import views
from praksis_nhn_nautobot.api.views import SambandMapDataAPIView, SambandSearchSuggestionsView

router = OrderedDefaultRouter()
# Register router viewsets
router.register("samband", views.SambandViewSet)

app_name = "praksis_nhn_nautobot_api"  # Use underscore instead of hyphen

# Define custom API endpoints first
urlpatterns = [
    path('samband/search-suggestions/', SambandSearchSuggestionsView.as_view(), name='samband_search_suggestions'),
    path('samband/map-data/', SambandMapDataAPIView.as_view(), name='samband_map_data'),
]

# Extend with router URLs - don't override
urlpatterns += router.urls
