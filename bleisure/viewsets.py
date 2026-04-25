"""
SubEvent ViewSet for complete CRUD management.
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Event, SubEvent
from .serializers import SubEventSerializer


class SubEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for complete SubEvent management (CRUD operations).
    
    Requires: Authentication (IsAuthenticated)
    
    Supports:
    - Create: POST /events/{event_id}/sub-events/
    - List: GET /events/{event_id}/sub-events/
    - Retrieve: GET /events/{event_id}/sub-events/{id}/
    - Update: PATCH /events/{event_id}/sub-events/{id}/
    - Delete: DELETE /events/{event_id}/sub-events/{id}/
    - Filter by type: ?type=agenda or ?type=side_event
    
    Validates:
    - No time overlaps
    - End time after start time
    - Parent event exists and is active
    """
    
    serializer_class = SubEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get SubEvents filtered by parent event and optional type parameter.
        """
        event_id = self.kwargs.get('event_id')
        queryset = SubEvent.objects.filter(event_id=event_id).order_by('start_time')
        
        # Filter by type if provided
        type_param = self.request.query_params.get('type')
        if type_param:
            queryset = queryset.filter(type=type_param)
        
        return queryset
    
    def get_event(self):
        """
        Get parent event and validate it exists and is active.
        Returns 404 if not found or soft-deleted.
        """
        return get_object_or_404(Event, id=self.kwargs['event_id'], is_active=True)
    
    def get_serializer_context(self):
        """
        Add parent event to serializer context for validation.
        """
        context = super().get_serializer_context()
        context['event'] = self.get_event()
        return context
    
    def perform_create(self, serializer):
        """
        Create SubEvent linked to parent event.
        """
        serializer.save(event=self.get_event())
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete SubEvent and return success response.
        """
        instance = self.get_object()
        instance_title = instance.title
        self.perform_destroy(instance)
        
        return Response(
            {
                'success': True,
                'message': f'SubEvent "{instance_title}" deleted successfully'
            },
            status=status.HTTP_200_OK
        )
    
    def perform_destroy(self, instance):
        """
        Delete SubEvent.
        """
        instance.delete()
