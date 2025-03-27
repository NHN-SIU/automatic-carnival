"""API serializers for praksis_nhn_nautobot."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from praksis_nhn_nautobot import models

class ParentSambandSerializer(NautobotModelSerializer):
    """Simplified serializer for parent connections."""
    
    class Meta:
        model = models.Samband
        fields = ['id', 'name', 'sambandsnummer']


class SambandSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """Samband Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.Samband
        fields = "__all__"