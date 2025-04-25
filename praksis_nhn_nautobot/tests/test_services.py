from django.test import TestCase
from praksis_nhn_nautobot.services.graph_service import SambandGraphService

"""Unit test for service module."""

class TestSambandGraphService(TestCase):
    """Tests for SambandGraphService."""

    def test_create_network_graph_empty(self):
        """Test creating a graph with empty data."""
        result = SambandGraphService.create_network_graph([])
        self.assertEqual(result, {"nodes": [], "edges": []})

    def test_create_network_graph_single_node(self):
        """Test creating a graph with a single node."""
        samband_data = [{
            "id": "1",
            "name": "Test Samband",
            "type": "Type1",
            "status": "Active",
            "sambandsnummer": "S123",
            "bandwidth_string": "100 Mbps",
            "vendor": "Vendor1",
            "location": "Location1",
            "transporttype": "Type1",
            "parents": []
        }]
        
        result = SambandGraphService.create_network_graph(samband_data)
        
        self.assertEqual(len(result["nodes"]), 1)
        self.assertEqual(len(result["edges"]), 0)
        self.assertEqual(result["nodes"][0]["id"], "1")
        self.assertEqual(result["nodes"][0]["label"], "Test Samband")

    def test_create_network_graph_with_connections(self):
        """Test creating a graph with parent-child relationships."""
        samband_data = [
            {
                "id": "1",
                "name": "Parent",
                "type": "Type1",
                "status": "Active",
                "sambandsnummer": "S123",
                "bandwidth_string": "100 Mbps",
                "vendor": "Vendor1",
                "location": "Location1",
                "transporttype": "Type1",
                "parents": []
            },
            {
                "id": "2",
                "name": "Child",
                "type": "Type2",
                "status": "Active",
                "sambandsnummer": "S456",
                "bandwidth_string": "200 Mbps",
                "vendor": "Vendor2",
                "location": "Location2",
                "transporttype": "Type2",
                "parents": [{"id": "1"}]
            }
        ]
        
        result = SambandGraphService.create_network_graph(samband_data)
        
        self.assertEqual(len(result["nodes"]), 2)
        self.assertEqual(len(result["edges"]), 1)
        self.assertEqual(result["edges"][0]["from"], "1")
        self.assertEqual(result["edges"][0]["to"], "2")