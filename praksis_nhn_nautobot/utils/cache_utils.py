"""Helper utilities for cross-view navigation with filter preservation."""

import uuid
from django.core.cache import cache

def cache_selection_and_filters(queryset, filter_params, timeout=3600):
    """
    Cache both the queryset selection and filter parameters.
    
    Args:
        queryset: The filtered queryset
        filter_params: Dictionary of active filter parameters
        timeout: Cache timeout in seconds (default: 1 hour)
        
    Returns:
        selection_id: Unique reference ID for this selection and filters
    """
    selection_id = uuid.uuid4().hex
    object_ids = list(queryset.values_list('id', flat=True))
    
    # Store both the object IDs and filter parameters
    cache_data = {
        'object_ids': object_ids,
        'filter_params': filter_params
    }
    
    cache_key = f"samband_selection_{selection_id}"
    cache.set(cache_key, cache_data, timeout)

    # Log the caching operation
    print(f"Cached selection {selection_id} with {len(object_ids)} objects and filters: {filter_params}")

    return selection_id

def get_cached_selection(selection_id):
    """
    Retrieve cached selection and filter data.
    
    Args:
        selection_id: The unique selection reference ID
        
    Returns:
        tuple of (object_ids, filter_params) or (None, None) if not found
    """
    if not selection_id:
        return None, None
        
    cache_key = f"samband_selection_{selection_id}"
    cached_data = cache.get(cache_key)
    
    if not cached_data:
        return None, None

    print(f"Retrieved selection {selection_id} with {cached_data.get('object_ids')} objects and filters: {cached_data.get('filter_params')}")
        
    return cached_data.get('object_ids'), cached_data.get('filter_params')