"""Unit tests for views."""

from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse

from nautobot.apps.testing import ViewTestCases

from praksis_nhn_nautobot import models, views
from praksis_nhn_nautobot.tests import fixtures
from nautobot.core.testing import ViewTestCases

from praksis_nhn_nautobot.models import Samband


class SambandUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Samband UI views."""

    model = Samband
    bulk_edit_url_name = "plugins:praksis_nhn_nautobot:samband_bulk_edit"
    bulk_delete_url_name = "plugins:praksis_nhn_nautobot:samband_bulk_delete"
    list_url_name = "plugins:praksis_nhn_nautobot:samband_list"
    add_url_name = "plugins:praksis_nhn_nautobot:samband_add"
    edit_url_name = "plugins:praksis_nhn_nautobot:samband_edit"
    detail_url_name = "plugins:praksis_nhn_nautobot:samband"
    delete_url_name = "plugins:praksis_nhn_nautobot:samband_delete"

    @classmethod
    def setUpTestData(cls):
        fixtures.create_samband()


class SambandGraphViewTest(TestCase):
    """Test the SambandGraphView."""

    @classmethod
    def setUpTestData(cls):
        cls.samband = models.Samband.objects.create(name="main")
        
        # Create parent-child relationships
        cls.parent1 = models.Samband.objects.create(name="Parent 1", sambandsnummer="P1")
        cls.parent2 = models.Samband.objects.create(name="Parent 2", sambandsnummer="P2")
        cls.child1 = models.Samband.objects.create(name="Child 1", sambandsnummer="C1")
        cls.child2 = models.Samband.objects.create(name="Child 2", sambandsnummer="C2")
        
        # Setup relationships
        cls.samband.parents.add(cls.parent1, cls.parent2)
        cls.samband.children.add(cls.child1, cls.child2)

    def setUp(self):
        self.factory = RequestFactory()
        self.view = views.SambandGraphView()

    def test_get_extra_context_default_parameters(self):
        """Test get_extra_context with default parameters."""
        request = self.factory.get(f'/samband/{self.samband.pk}/graph/')
        context = self.view.get_extra_context(request, self.samband)
        
        # Verify context keys
        self.assertIn('graph_data', context)
        self.assertIn('current_depth', context)
        self.assertIn('current_mode', context)
        self.assertIn('depth_options', context)
        self.assertIn('samband_json', context)
        
        # Verify default values
        self.assertEqual(context['current_depth'], 2)
        self.assertEqual(context['current_mode'], 'hierarchy')
        
        # Check graph data structure
        graph_data = context['graph_data']
        self.assertIn('nodes', graph_data)
        self.assertIn('links', graph_data)
        
        # Should have 5 nodes: current, 2 parents, 2 children
        self.assertEqual(len(graph_data['nodes']), 5)
        self.assertEqual(len(graph_data['links']), 4)

    def test_get_extra_context_parents_mode(self):
        """Test get_extra_context with parents mode."""
        request = self.factory.get(f'/samband/{self.samband.pk}/graph/?mode=parents')
        context = self.view.get_extra_context(request, self.samband)
        
        # Check if only parent relationships are included
        graph_data = context['graph_data']
        self.assertEqual(context['current_mode'], 'parents')
        
        # Should have 3 nodes: current and 2 parents
        self.assertEqual(len(graph_data['nodes']), 3)
        # Should have 2 links to parents
        self.assertEqual(len(graph_data['links']), 2)

    def test_get_extra_context_children_mode(self):
        """Test get_extra_context with children mode."""
        request = self.factory.get(f'/samband/{self.samband.pk}/graph/?mode=children')
        context = self.view.get_extra_context(request, self.samband)
        
        # Check if only children relationships are included
        graph_data = context['graph_data']
        self.assertEqual(context['current_mode'], 'children')
        
        # Should have 3 nodes: current and 2 children
        self.assertEqual(len(graph_data['nodes']), 3)
        # Should have 2 links to children
        self.assertEqual(len(graph_data['links']), 2)

    def test_get_extra_context_custom_depth(self):
        """Test get_extra_context with custom depth."""
        request = self.factory.get(f'/samband/{self.samband.pk}/graph/?depth=1')
        context = self.view.get_extra_context(request, self.samband)
        
        # Verify custom depth is used
        self.assertEqual(context['current_depth'], 1)

    def test_get_relation_tree_with_cycles(self):
        """Test _get_relation_tree handles cyclic relationships."""
        # Create a cyclic relationship
        self.parent1.parents.add(self.samband)
        
        # This should not cause an infinite recursion
        tree = self.view._get_relation_tree(self.samband, 'parents')
        
        # Tree should still be created
        self.assertIsNotNone(tree)

    def test_flatten_tree(self):
        """Test _flatten_tree method."""
        tree = [
            {'id': '1', 'name': 'Test 1', 'parents': [{'id': '2', 'name': 'Test 2'}]},
            {'id': '3', 'name': 'Test 3', 'children': [{'id': '4', 'name': 'Test 4'}]}
        ]
        flat_tree = self.view._flatten_tree(tree)
        
        # Check that nested data is removed
        self.assertEqual(len(flat_tree), 2)
        for item in flat_tree:
            self.assertNotIn('parents', item)
            self.assertNotIn('children', item)

    def test_prepare_graph_data(self):
        """Test _prepare_graph_data method."""
        parent_tree = [{'id': '1', 'name': 'Parent'}]
        child_tree = [{'id': '2', 'name': 'Child'}]
        
        graph_data = self.view._prepare_graph_data(self.samband, parent_tree, child_tree)
        
        # Should have 3 nodes: current, parent, and child
        self.assertEqual(len(graph_data['nodes']), 3)
        # Should have 2 links: one to parent, one to child
        self.assertEqual(len(graph_data['links']), 2)
