"""API views for praksis_nhn_nautobot."""

from rest_framework.decorators import action
from rest_framework.response import Response
from nautobot.apps.api import NautobotModelViewSet

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.api import serializers

from praksis_nhn_nautobot.models import Samband
from praksis_nhn_nautobot.services.graph_service import SambandGraphService
from django.http import JsonResponse

class SambandViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """Samband viewset."""

    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    filterset_class = filters.SambandFilterSet