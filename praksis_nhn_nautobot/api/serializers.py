"""API serializers for praksis_nhn_nautobot."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from praksis_nhn_nautobot import models

class SambandSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """Samband Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.Samband
        fields = "__all__"