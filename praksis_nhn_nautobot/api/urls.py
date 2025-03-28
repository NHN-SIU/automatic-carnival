"""Django API urlpatterns declaration for praksis_nhn_nautobot app."""

from nautobot.apps.api import OrderedDefaultRouter

from praksis_nhn_nautobot.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("samband", views.SambandViewSet)

app_name = "praksis_nhn_nautobot-api"
urlpatterns = router.urls
