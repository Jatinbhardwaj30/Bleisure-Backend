from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class ConferenceCursorPagination(CursorPagination):
    """
    Custom cursor-based pagination for Conference list API.
    Provides scalable pagination for large datasets.
    
    Features:
    - Cursor-based, not affected by existing data changes
    - Ordering by created_at (latest first)
    - Page size of 10 (configurable)
    - Safe for concurrent modifications
    - Includes total count for UI display
    """
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    cursor_query_description = 'The pagination cursor value.'
    template = 'rest_framework/pagination/numbers.html'
    invalid_cursor_message = 'Invalid cursor value.'
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, else return None.
        Supports optional page_size query parameter.
        Stores total count for response.
        """
        # Allow custom page size from query params
        self.page_size = request.query_params.get(self.page_size_query_param, self.page_size)
        
        try:
            self.page_size = int(self.page_size)
        except (ValueError, TypeError):
            self.page_size = 10
        
        # Ensure page size is within limits
        if self.page_size > self.max_page_size:
            self.page_size = self.max_page_size
        
        if self.page_size < 1:
            self.page_size = 10
        
        # Store total count for cursor pagination
        self.count = queryset.count()
        
        return super().paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):
        """
        Return paginated response with cursor URLs and total count.
        """
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'results': data
        })
