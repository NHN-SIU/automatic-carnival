"""Django urlpatterns declaration for praksis_nhn_nautobot app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from praksis_nhn_nautobot import views

app_name = "praksis_nhn_nautobot"
router = NautobotUIViewSetRouter()

router.register("samband", views.SambandUIViewSet)


urlpatterns = [
    path('samband/search-suggestions/', views.SambandSearchSuggestionsView.as_view(), name='samband_search_suggestions'),
    path("docs/", RedirectView.as_view(url=static("praksis_nhn_nautobot/docs/index.html")), name="docs"),
    path("samband/<uuid:pk>/graph/", views.SambandGraphView.as_view(), name="samband_graph"),
    path("samband/map/<uuid:pk>/", views.SambandMapView.as_view(), name="samband_map"),
    path('samband/map/', views.SambandClientMapView.as_view(), name='samband_client_map'),
    path('samband/map-data/', views.SambandMapDataAPIView.as_view(), name='samband_map_data'),
]

urlpatterns += router.urls
