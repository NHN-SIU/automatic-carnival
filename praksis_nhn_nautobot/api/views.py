"""API views for praksis_nhn_nautobot."""

from rest_framework.decorators import action
from rest_framework.response import Response
from nautobot.apps.api import NautobotModelViewSet

from praksis_nhn_nautobot import filters, models
from praksis_nhn_nautobot.api import serializers

from praksis_nhn_nautobot.models import Samband
from praksis_nhn_nautobot.services.graph_service import SambandGraphService
from django.http import JsonResponse

from django.views import View
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt

class SambandViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """Samband viewset."""

    queryset = models.Samband.objects.all()
    serializer_class = serializers.SambandSerializer
    filterset_class = filters.SambandFilterSet


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
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


class SambandMapDataAPIView(View):
    """API view that returns sambands data as JSON for client-side rendering."""
    
    def get(self, request):
        # Get filter parameters from request
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = request.GET.get('radius')
        
        # Handle connection detail request
        connection_id = request.GET.get('connection_id')

        # this is for 1 specific connection
        if connection_id:
            try:
                samband = Samband.objects.get(pk=connection_id)
                
                # Parse coordinates - only do this once
                point_a_coords = None
                if samband.pop_a_geo_string:
                    a_lat, a_lng = parse_geo_coordinates(samband.pop_a_geo_string)
                    if a_lat is not None and a_lng is not None:
                        point_a_coords = [a_lat, a_lng]
                
                point_b_coords = None
                if samband.pop_b_geo_string:
                    b_lat, b_lng = parse_geo_coordinates(samband.pop_b_geo_string)
                    if b_lat is not None and b_lng is not None:
                        point_b_coords = [b_lat, b_lng]
                
                # Return simplified connection information
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
                    'pop_a_coords': point_a_coords,  # Just include coordinates directly
                    'pop_b_address': samband.pop_b_address_string,
                    'pop_b_category': samband.pop_b_category,
                    'pop_b_room': samband.pop_b_room,
                    'pop_b_coords': point_b_coords,  # Just include coordinates directly
                    'location': samband.location,
                    'location_type': samband.location_type,
                    'transport_type': samband.transporttype
                })
            except Samband.DoesNotExist:
                return JsonResponse({'error': 'Connection not found'}, status=404)
        
        # Handle multiple filter selections (keep existing filter code)
        vendors = request.GET.getlist('vendor')
        statuses = request.GET.getlist('status')
        citylist = request.GET.getlist('location')
        location_types = request.GET.getlist('location_type')
        transport_types = request.GET.getlist('transporttype')
        type = request.GET.getlist('type')

        print(f"Vendors: {vendors}")
        print(f"Statuses: {statuses}")
        print(f"Citylist: {citylist}")
        print(f"Location Types: {location_types}")
        print(f"Transport Types: {transport_types}")
        print(f"Type: {type}")
        
        # Start with all connections
        sambands = Samband.objects.all()
        
        # Apply vendor and status filters (keep existing filter code)
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
        
        if type:
            sambands = sambands.filter(type__in=type)
        

        # Process distance filtering (keep existing distance calculation code)
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
        
        include_fields = request.GET.getlist('include_fields', [])
        
        connections = []
        
        for samband in sambands:
            # Extract coordinates for both points
            point_a_coords = None
            if samband.pop_a_geo_string:
                a_lat, a_lng = parse_geo_coordinates(samband.pop_a_geo_string)
                if a_lat is not None and a_lng is not None:
                    point_a_coords = [a_lat, a_lng]
            
            point_b_coords = None
            if samband.pop_b_geo_string:
                b_lat, b_lng = parse_geo_coordinates(samband.pop_b_geo_string)
                if b_lat is not None and b_lng is not None:
                    point_b_coords = [b_lat, b_lng]
            
            # Only include the connection if both points have valid coordinates
            if point_a_coords and point_b_coords:
                # Create the basic connection object with minimal data
                connection = {
                    'id': str(samband.pk),
                    'name': samband.name,
                    'point_a': {
                        'name': samband.name,
                        'location': point_a_coords,
                        'category': samband.pop_a_category,
                        # Remove address and room fields to reduce payload size
                    },
                    'point_b': {
                        'name': samband.name,
                        'location': point_b_coords,
                        'category': samband.pop_b_category,
                        # Remove address and room fields to reduce payload size
                    },
                    'status': samband.status,
                    'location_type': samband.location_type,
                }
                
                # Add any additional requested fields
                for field in include_fields:
                    # if field == 'status' and samband.status:
                    #     connection['status'] = samband.status
                    if field == 'vendor' and samband.vendor:
                        connection['vendor'] = samband.vendor
                    elif field == 'bandwidth' and samband.bandwidth_string:
                        connection['bandwidth'] = samband.bandwidth_string
                    elif field == 'reference' and samband.sambandsnummer:
                        connection['reference'] = samband.sambandsnummer
                    elif field == 'type' and samband.type:
                        connection['type'] = samband.type
                    elif field == 'location' and samband.location:
                        connection['location'] = samband.location
                    # elif field == 'location_type' and samband.location_type:
                    #     connection['location_type'] = samband.location_type
                    elif field == 'transporttype' and samband.transporttype:
                        connection['transporttype'] = samband.transporttype
                
                connections.append(connection)
        
        response_data = {
            'connections': connections,
            'count': len(connections),
            'filter_active': bool(vendors or statuses or citylist or location_types or transport_types or (lat and lng and radius))
        }
        
        # Add a radius circle if filtering by location
        if lat and lng and radius:
            response_data['radius'] = {
                'location': [float(lat), float(lng)],
                'radius_km': float(radius)
            }
        
        return JsonResponse(response_data)

class SambandSearchSuggestionsView(View):
    """Returns connection name suggestions for autocomplete."""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 2:
            return JsonResponse({'suggestions': []})
            
        # Search connections by name or location
        connections = Samband.objects.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(sambandsnummer__icontains=query)
        )[:10]
        
        suggestions = []
        for conn in connections:
            suggestions.append({
                'id': str(conn.pk),
                'name': conn.name,
                'location': conn.location,
                'status': conn.status
            })
            
        return JsonResponse({'suggestions': suggestions})