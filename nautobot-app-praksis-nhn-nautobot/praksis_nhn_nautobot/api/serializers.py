"""API serializers for praksis_nhn_nautobot.
Forteller Django hvordan den tar JSON data og hvordan oversette
det til en database-modell, eller omvendt. 
"""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from praksis_nhn_nautobot import models

class ParentNHNModelSerializer(NautobotModelSerializer):
    """Simplified serializer for parent connections."""
    
    class Meta:
        model = models.NHNModel
        fields = ['id', 'name']

class NHNModelSerializer(NautobotModelSerializer):
    """NHNModel serializer."""
    
    parents = ParentNHNModelSerializer(many=True, read_only=True)
    children = ParentNHNModelSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.NHNModel
        fields = "__all__"