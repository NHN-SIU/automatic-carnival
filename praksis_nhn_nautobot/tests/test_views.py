from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.urls import reverse
from praksis_nhn_nautobot.models import Samband
from praksis_nhn_nautobot.views import SambandGraphFocusView, SambandGraphView

"""Unit tests for views."""

class SambandGraphFocusViewTest(TestCase):
    """Tests for SambandGraphFocusView."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        # Create a mock Samband object
        self.samband = MagicMock(spec=Samband)
        self.samband.pk = 1
        
        # Setup patches for the view's dependencies
        self.get_relations_patch = patch('praksis_nhn_nautobot.services.graph_service.SambandGraphService.get_relations')
        self.create_network_graph_patch = patch('praksis_nhn_nautobot.services.graph_service.SambandGraphService.create_network_graph')
        self.serializer_patch = patch('praksis_nhn_nautobot.views.SambandSerializer')
        
        # Start patches and get mocks
        self.mock_get_relations = self.get_relations_patch.start()
        self.mock_create_network_graph = self.create_network_graph_patch.start()
        self.mock_serializer = self.serializer_patch.start()
        
        # Configure return values
        self.mock_get_relations.return_value = [self.samband]
        self.mock_serializer.return_value.data = ['serialized_data']
        self.mock_create_network_graph.return_value = {'nodes': [], 'edges': []}
        
        # Mock queryset get method
        self.queryset_patch = patch('praksis_nhn_nautobot.models.Samband.objects.get')
        self.mock_queryset_get = self.queryset_patch.start()
        self.mock_queryset_get.return_value = self.samband
    
    def tearDown(self):
        """Clean up patchers."""
        self.get_relations_patch.stop()
        self.create_network_graph_patch.stop()
        self.serializer_patch.stop()
        self.queryset_patch.stop()
    
    def test_get_extra_context_default_depth(self):
        """Test get_extra_context with default depth."""
        # Set up the view
        view = SambandGraphFocusView()
        view.kwargs = {'pk': 1}
        view.request = self.factory.get('/dummy/url/')
        
        # Call the method
        context = view.get_extra_context(view.request, self.samband)
        
        # Verify the method called services with correct parameters
        self.mock_get_relations.assert_called_once_with(self.samband, 2)
        self.mock_create_network_graph.assert_called_once_with(['serialized_data'])
        
        # Verify context contains expected data
        self.assertIn('network_data', context)
        self.assertIn('network_options', context)
        self.assertEqual(context['depth'], 2)

    
    def test_get_extra_context_custom_depth(self):
        """Test get_extra_context with custom depth."""
        # Set up the view
        view = SambandGraphFocusView()
        view.kwargs = {'pk': 1}
        view.request = self.factory.get('/dummy/url/?depth=3')
        
        # Call the method
        context = view.get_extra_context(view.request, self.samband)
        
        # Verify the method called services with custom depth
        self.mock_get_relations.assert_called_once_with(self.samband, 3)
        
        # Verify context contains expected data with custom depth
        self.assertEqual(context['depth'], 3)
    
    def test_template_name(self):
        """Test the template name is correctly set."""
        view = SambandGraphFocusView()
        self.assertEqual(view.template_name, "praksis_nhn_nautobot/focus_graph.html")


class SambandGraphViewTest(TestCase):
    """Tests for SambandGraphView."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        
        # Setup patches for the view's dependencies
        self.filterset_patch = patch('praksis_nhn_nautobot.filters.SambandFilterSet')
        self.create_network_graph_patch = patch('praksis_nhn_nautobot.services.graph_service.SambandGraphService.create_network_graph')
        self.serializer_patch = patch('praksis_nhn_nautobot.views.SambandSerializer')
        self.queryset_patch = patch('praksis_nhn_nautobot.models.Samband.objects.all')
        
        # Start patches and get mocks
        self.mock_filterset = self.filterset_patch.start()
        self.mock_create_network_graph = self.create_network_graph_patch.start()
        self.mock_serializer = self.serializer_patch.start()
        self.mock_queryset = self.queryset_patch.start()
        
        # Configure return values
        filterset_instance = self.mock_filterset.return_value
        filterset_instance.qs = [MagicMock(spec=Samband)]
        
        self.mock_serializer.return_value.data = ['serialized_data']
        self.mock_create_network_graph.return_value = {'nodes': [], 'edges': []}
    
    def tearDown(self):
        """Clean up patchers."""
        self.filterset_patch.stop()
        self.create_network_graph_patch.stop()
        self.serializer_patch.stop()
        self.queryset_patch.stop()
    
    def test_get(self):
        """Test the get method correctly renders the template with context."""
        with patch('praksis_nhn_nautobot.views.render') as mock_render:
            # Set up the view
            view = SambandGraphView()
            request = self.factory.get('/dummy/url/')
            view.request = request
            
            # Call the method
            view.get(request)
            
            # Verify render was called with correct template
            mock_render.assert_called_once()
            template_name = mock_render.call_args[0][1]
            self.assertEqual(template_name, "praksis_nhn_nautobot/network_graph.html")
    
    def test_get_queryset(self):
        """Test the get_queryset method correctly applies filters."""
        # Set up the view
        view = SambandGraphView()
        view.request = self.factory.get('/dummy/url/?status=Active')
        
        # Call the method
        queryset = view.get_queryset()
        
        # Verify filterset was created with correct parameters
        self.mock_filterset.assert_called_once()
        call_kwargs = self.mock_filterset.call_args[1]
        self.assertEqual(call_kwargs['data'], {'status': ['Active']})
        self.assertEqual(call_kwargs['request'], view.request)
        
        # Verify queryset is the filtered qs
        self.assertEqual(queryset, self.mock_filterset.return_value.qs)
    
    def test_get_context_data(self):
        """Test the get_context_data method returns correct context."""
        # Set up the view
        view = SambandGraphView()
        view.request = self.factory.get('/dummy/url/')
        
        # Call the method
        context = view.get_context_data()
        
        # Verify serializer was created with correct parameters
        self.mock_serializer.assert_called_once()
        
        # Verify create_network_graph was called with serialized data
        self.mock_create_network_graph.assert_called_once_with(['serialized_data'])
        
        # Verify context contains expected data
        self.assertIn('network_data', context)
        self.assertIn('network_options', context)