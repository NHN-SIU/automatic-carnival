"""Views for praksis_nhn_nautobot."""

from nautobot.apps.views import NautobotUIViewSet

from praksis_nhn_nautobot import filters, forms, models, tables
from praksis_nhn_nautobot.api import serializers


class NHNModelUIViewSet(NautobotUIViewSet):
    """ViewSet for NHNModel views."""

    bulk_update_form_class = forms.NHNModelBulkEditForm
    filterset_class = filters.NHNModelFilterSet
    filterset_form_class = forms.NHNModelFilterForm
    form_class = forms.NHNModelForm
    lookup_field = "pk"
    queryset = models.NHNModel.objects.all()
    serializer_class = serializers.NHNModelSerializer
    table_class = tables.NHNModelTable
