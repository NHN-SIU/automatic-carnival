"""API views for praksis_nhn_nautobot."""

from nautobot.apps.api import NautobotModelViewSet

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.api import serializers


class SambandViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """Samband viewset."""

    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    filterset_class = filters.SambandFilterSet
