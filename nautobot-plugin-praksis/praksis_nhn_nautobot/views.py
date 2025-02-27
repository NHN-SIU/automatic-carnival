"""Views for praksis_nhn_nautobot."""

from nautobot.apps.views import NautobotUIViewSet

from praksis_nhn_nautobot import filters, forms, models, tables
from praksis_nhn_nautobot.api import serializers


class SambandUIViewSet(NautobotUIViewSet):
    """ViewSet for Samband views."""

    bulk_update_form_class = forms.SambandBulkEditForm
    filterset_class = filters.SambandFilterSet
    filterset_form_class = forms.SambandFilterForm
    form_class = forms.SambandForm
    lookup_field = "pk"
    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    table_class = tables.SambandTable
