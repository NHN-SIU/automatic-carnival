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
    path("docs/", RedirectView.as_view(url=static("praksis_nhn_nautobot/docs/index.html")), name="docs"),
    path("samband/<uuid:pk>/graph/", views.SambandGraphView.as_view(), name="Samband_graph"),
]

urlpatterns += router.urls
