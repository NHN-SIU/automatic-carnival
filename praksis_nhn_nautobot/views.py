"""Views for praksis_nhn_nautobot."""

from nautobot.apps.views import NautobotUIViewSet
from django.views.generic import DetailView, View, TemplateView
from django.shortcuts import render
from django.http import JsonResponse

from praksis_nhn_nautobot import filters, forms, models, tables
from praksis_nhn_nautobot.api import serializers
from math import radians, cos, sin, asin, sqrt

from .models import Samband


class SambandUIViewSet(NautobotUIViewSet):
    """
    NautobotUIViewSet allows us to modify the existing UI of Nautobot by extending built-in views with custom forms, filters, tables, and templates.

    This viewset defines the user interface
    for interacting with Samband objects, including listing, creating, editing, and deleting entries.
    It uses custom forms for single and bulk editing, a filterset for list filtering, a serializer
    for API support, and a table definition for how Samband objects are displayed in the list view.
    For more info, check out:
    https://docs.nautobot.com/projects/core/en/stable/development/apps/api/views/nautobotuiviewset/
    """

    bulk_update_form_class = forms.SambandBulkEditForm
    filterset_class = filters.SambandFilterSet
    filterset_form_class = forms.SambandFilterForm
    form_class = forms.SambandForm
    lookup_field = "pk"
    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    table_class = tables.SambandTable


def parse_geo_coordinates(geo_string):
    """Parse geographic coordinates in various formats."""
    if not geo_string:
        return None, None
        
    try:
        # Handle format: "60.3927° N, 5.3245° E"
        if '°' in geo_string:
            # Split into lat and lng parts
            parts = geo_string.split(',')
            if len(parts) < 2:
                return None, None
                
            # Parse latitude
            lat_part = parts[0].strip()
            lat_value = float(lat_part.split('°')[0].strip())
            if 'S' in lat_part:
                lat_value = -lat_value  # Southern hemisphere is negative
                
            # Parse longitude
            lng_part = parts[1].strip()
            lng_value = float(lng_part.split('°')[0].strip())
            if 'W' in lng_part:
                lng_value = -lng_value  # Western hemisphere is negative
                
            return lat_value, lng_value
            
        # Handle simple "lat, lng" format
        else:
            parts = geo_string.split(',')
            if len(parts) >= 2:
                return float(parts[0].strip()), float(parts[1].strip())
                
    except (ValueError, IndexError) as e:
        print(f"Error parsing geo_string '{geo_string}': {e}")
        
    return None, None


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points using Haversine formula."""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r


class SambandMapView(DetailView):
    """View for displaying a map for a single Samband instance."""
    model = Samband
    template_name = "praksis_nhn_nautobot/samband_map.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        samband = self.get_object()
        
        # Process the single samband into map features
        features = []
        connection_points = []
        
        # Process Point A
        if samband.pop_a_geo_string:
            a_lat, a_lng = parse_geo_coordinates(samband.pop_a_geo_string)
            if a_lat is not None and a_lng is not None:
                point_data = {
                    'type': 'point',
                    'point_type': 'A',
                    'location': [a_lat, a_lng],
                    'name': samband.name,
                    'address': samband.pop_a_address_string,
                    'category': samband.pop_a_category,
                    'room': samband.pop_a_room,
                    'id': str(samband.pk)
                }
                features.append(point_data)
                connection_points.append([a_lat, a_lng])
        
        # Process Point B
        if samband.pop_b_geo_string:
            b_lat, b_lng = parse_geo_coordinates(samband.pop_b_geo_string)
            if b_lat is not None and b_lng is not None:
                point_data = {
                    'type': 'point',
                    'point_type': 'B',
                    'location': [b_lat, b_lng],
                    'name': samband.name,
                    'address': samband.pop_b_address_string,
                    'category': samband.pop_b_category,
                    'room': samband.pop_b_room,
                    'id': str(samband.pk)
                }
                features.append(point_data)
                connection_points.append([b_lat, b_lng])
        
        # Add connection line if both points exist
        if len(connection_points) == 2:
            line_data = {
                'type': 'line',
                'points': connection_points,
                'name': samband.name,
                'id': str(samband.pk)
            }
            features.append(line_data)
        
        # Add samband details and map features to context
        context['samband'] = samband
        context['map_data'] = {
            'features': features,
            'count': 1,
            'samband_details': {
                'name': samband.name,
                'vendor': samband.vendor,
                'status': samband.status,
                'bandwidth': samband.bandwidth_string,
                'reference': samband.sambandsnummer,
                'type_name': samband.type,
                'location': samband.location,
                'location_type': samband.location_type,
                'transport_type': samband.transporttype
            }
        }
        
        return context


class SambandMapDataAPIView(View):
    """API view that returns sambands data as JSON for client-side rendering."""
    
    def get(self, request):
        # Get filter parameters from request
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = request.GET.get('radius')
        
        # Handle connection detail request
        connection_id = request.GET.get('connection_id')
        if connection_id:
            try:
                samband = Samband.objects.get(pk=connection_id)
                # Return detailed connection information
                return JsonResponse({
                    'name': samband.name,
                    'vendor': samband.vendor,
                    'status': samband.status,
                    'bandwidth': samband.bandwidth_string,
                    'reference': samband.sambandsnummer,
                    'type_name': samband.type,
                    'pop_a_address': samband.pop_a_address_string,
                    'pop_a_category': samband.pop_a_category,
                    'pop_a_room': samband.pop_a_room,
                    'pop_b_address': samband.pop_b_address_string,
                    'pop_b_category': samband.pop_b_category,
                    'pop_b_room': samband.pop_b_room,
                    'location': samband.location,
                    'location_type': samband.location_type,
                    'transport_type': samband.transporttype,
                })
            except Samband.DoesNotExist:
                return JsonResponse({'error': 'Connection not found'}, status=404)
        
        # Handle multiple filter selections
        vendors = request.GET.getlist('vendors')
        statuses = request.GET.getlist('statuses')
        citylist = request.GET.getlist('location')
        location_types = request.GET.getlist('location_type')
        transport_types = request.GET.getlist('transport_type')
        
        # Start with all sambands
        sambands = Samband.objects.all()
        
        # Apply vendor and status filters
        if vendors:
            sambands = sambands.filter(vendor__in=vendors)
            
        if statuses:
            sambands = sambands.filter(status__in=statuses)
        
        if citylist:
            sambands = sambands.filter(location__in=citylist)
        
        if location_types:
            sambands = sambands.filter(location_type__in=location_types)

        if transport_types:
            sambands = sambands.filter(transporttype__in=transport_types)
        
        # Process distance filtering
        if lat and lng and radius:
            try:
                center_lat = float(lat)
                center_lng = float(lng)
                radius_km = float(radius)
                
                # Filter by distance
                filtered_by_distance = []
                
                for samband in sambands:
                    points_in_radius = False
                    
                    # Check point A
                    if samband.pop_a_geo_string:
                        a_lat, a_lng = parse_geo_coordinates(samband.pop_a_geo_string)
                        if a_lat is not None and a_lng is not None:
                            distance = calculate_distance(center_lat, center_lng, a_lat, a_lng)
                            if distance <= radius_km:
                                points_in_radius = True
                    
                    # Check point B
                    if not points_in_radius and samband.pop_b_geo_string:
                        b_lat, b_lng = parse_geo_coordinates(samband.pop_b_geo_string)
                        if b_lat is not None and b_lng is not None:
                            distance = calculate_distance(center_lat, center_lng, b_lat, b_lng)
                            if distance <= radius_km:
                                points_in_radius = True
                    
                    if points_in_radius:
                        filtered_by_distance.append(samband)
                
                sambands = filtered_by_distance
                
            except (ValueError, TypeError) as e:
                # Log the error for debugging
                print(f"Error processing geo filter: {e}")
        
        # Build response data with minimal information
        features = []
        center_points = []
        
        # Process each samband
        for samband in sambands:
            connection_points = []
            
            # Process Point A with minimal data
            if samband.pop_a_geo_string:
                a_lat, a_lng = parse_geo_coordinates(samband.pop_a_geo_string)
                if a_lat is not None and a_lng is not None:
                    point_data = {
                        'type': 'point',
                        'point_type': 'A',
                        'location': [a_lat, a_lng],
                        'name': samband.name,
                        'id': str(samband.pk)
                    }
                    features.append(point_data)
                    connection_points.append([a_lat, a_lng])
                    center_points.append([a_lat, a_lng])
            
            # Process Point B with minimal data
            if samband.pop_b_geo_string:
                b_lat, b_lng = parse_geo_coordinates(samband.pop_b_geo_string)
                if b_lat is not None and b_lng is not None:
                    point_data = {
                        'type': 'point',
                        'point_type': 'B',
                        'location': [b_lat, b_lng],
                        'name': samband.name,
                        'id': str(samband.pk)
                    }
                    features.append(point_data)
                    connection_points.append([b_lat, b_lng])
                    center_points.append([b_lat, b_lng])
            
            # Add connection line with minimal data
            if len(connection_points) == 2:
                line_data = {
                    'type': 'line',
                    'points': connection_points,
                    'name': samband.name,
                    'id': str(samband.pk)
                }
                features.append(line_data)
        
        # Add a radius circle if filtering by location
        if lat and lng and radius:
            features.append({
                'type': 'radius',
                'location': [float(lat), float(lng)],
                'radius': float(radius) * 1000  # Convert to meters
            })
        
        # Return the minimal data
        response_data = {
            'features': features,
            'count': len(sambands),
            'filter_active': bool(vendors or statuses or citylist or location_types or transport_types or (lat and lng and radius))
        }
        
        return JsonResponse(response_data)


class SambandClientMapView(TemplateView):
    """View for displaying a map using client-side rendering."""
    template_name = "praksis_nhn_nautobot/samband_map_clientside.html"
    
    def get_filter_options(self):
        # Get unique filter values
        vendors = Samband.objects.values_list('vendor', flat=True).distinct().order_by('vendor')
        statuses = Samband.objects.values_list('status', flat=True).distinct().order_by('status')
        citylist = Samband.objects.values_list('location', flat=True).distinct().order_by('location')
        location_types = Samband.objects.values_list('location_type', flat=True).distinct().order_by('location_type')
        transport_types = Samband.objects.values_list('transporttype', flat=True).distinct().order_by('transporttype')

        # Filter out None/empty values
        vendors = [v for v in vendors if v]
        statuses = [s for s in statuses if s]
        citylist = [c for c in citylist if c]
        location_types = [lt for lt in location_types if lt]
        transport_types = [tt for tt in transport_types if tt]
        
        return {
            'vendors': vendors,
            'statuses': statuses,
            'citylist': citylist,
            'location_types': location_types,
            'transport_types': transport_types
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters from request
        lat = self.request.GET.get('lat')
        lng = self.request.GET.get('lng')
        radius = self.request.GET.get('radius')
        
        # Handle multiple selections
        vendors = self.request.GET.getlist('vendors')
        statuses = self.request.GET.getlist('statuses')
        citylist = self.request.GET.getlist('location')
        location_types = self.request.GET.getlist('location_type')
        transport_types = self.request.GET.getlist('transport_type')
        
        # Get filter options
        filter_options = self.get_filter_options()
        context.update(filter_options)
        
        # Add selected values to context
        if vendors:
            context['selected_vendors'] = vendors
        if statuses:
            context['selected_statuses'] = statuses
        if citylist:
            context['selected_citylist'] = citylist
        if location_types:
            context['selected_location_types'] = location_types
        if transport_types:
            context['selected_transport_types'] = transport_types
        
        # Add location parameters to context
        if lat:
            context['lat'] = lat
        if lng:
            context['lng'] = lng
        if radius:
            context['radius'] = radius
        else:
            context['radius'] = '50'  # Default radius
        
        context['title'] = 'Network Connections Map'
        
        return context
