"""Django urlpatterns declaration for praksis_nhn_nautobot app."""

from django.templatetags.static import static
from django.urls import path, include
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from praksis_nhn_nautobot import views

app_name = "praksis_nhn_nautobot"
router = NautobotUIViewSetRouter()

router.register("samband", views.SambandUIViewSet)

urlpatterns = [
    path('api/', include('praksis_nhn_nautobot.api.urls')),
    
    path("docs/", RedirectView.as_view(url=static("praksis_nhn_nautobot/docs/index.html")), name="docs"),
    path("samband/graph/<uuid:pk>/", views.SambandGraphFocusView.as_view(), name="samband_graph_focus"),
    path("samband/graph/", views.SambandGraphView.as_view(), name="samband_graph"),
    path("samband/map/<uuid:pk>/", views.SambandMapView.as_view(), name="samband_map"),
    path('samband/map/', views.SambandMultipleMapView.as_view(), name='samband_client_map'),
]

urlpatterns += router.urls
