"""API views for praksis_nhn_nautobot."""

from nautobot.apps.api import NautobotModelViewSet

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.api import serializers


class NHNModelViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """NHNModel viewset."""

    queryset = models.NHNModel.objects.all()
    serializer_class = serializers.NHNModelSerializer
    filterset_class = filters.NHNModelFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
