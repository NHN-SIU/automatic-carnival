"""Django urlpatterns declaration for praksis_nhn_nautobot app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from praksis_nhn_nautobot import views

router = NautobotUIViewSetRouter()

router.register("nhnmodel", views.NHNModelUIViewSet)

urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("praksis_nhn_nautobot/docs/index.html")), name="docs"),
    path("nhnmodel/<uuid:pk>/graph/", views.NHNModelGraphView.as_view(), name="nhnmodel_graph"),
]

urlpatterns += router.urls
