"""API serializers for praksis_nhn_nautobot."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from praksis_nhn_nautobot import models


class NHNModelSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """NHNModel Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.NHNModel
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []
