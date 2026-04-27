"""
SubEvent ViewSet for complete CRUD management.
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Event, SubEvent, Speaker, Exhibitor, Deal
from .serializers import SubEventSerializer, SpeakerSerializer, ExhibitorSerializer, DealSerializer


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


# ==================== SPEAKER VIEWSET ====================

class SpeakerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Speaker management (CRUD operations).
    
    Requires: Authentication (IsAuthenticated)
    
    Supports:
    - Create: POST /events/{event_id}/speakers/
    - List: GET /events/{event_id}/speakers/
    - Retrieve: GET /events/{event_id}/speakers/{id}/
    - Update: PATCH /events/{event_id}/speakers/{id}/
    - Delete: DELETE /events/{event_id}/speakers/{id}/
    """
    
    serializer_class = SpeakerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get Speakers filtered by parent event.
        """
        event_id = self.kwargs.get('event_id')
        return Speaker.objects.filter(event_id=event_id).order_by('name')
    
    def get_event(self):
        """
        Get parent event and validate it exists and is active.
        Returns 404 if not found or soft-deleted.
        """
        return get_object_or_404(Event, id=self.kwargs['event_id'], is_active=True)
    
    def perform_create(self, serializer):
        """
        Create Speaker linked to parent event.
        """
        serializer.save(event=self.get_event())
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete Speaker and return success response.
        """
        instance = self.get_object()
        speaker_name = instance.name
        self.perform_destroy(instance)
        
        return Response(
            {
                'success': True,
                'message': f'Speaker "{speaker_name}" deleted successfully'
            },
            status=status.HTTP_200_OK
        )


# ==================== EXHIBITOR VIEWSET ====================

class ExhibitorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Exhibitor management (CRUD operations).
    
    Requires: Authentication (IsAuthenticated)
    
    Supports:
    - Create: POST /events/{event_id}/exhibitors/
    - List: GET /events/{event_id}/exhibitors/
    - Retrieve: GET /events/{event_id}/exhibitors/{id}/
    - Update: PATCH /events/{event_id}/exhibitors/{id}/
    - Delete: DELETE /events/{event_id}/exhibitors/{id}/
    """
    
    serializer_class = ExhibitorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get Exhibitors filtered by parent event.
        """
        event_id = self.kwargs.get('event_id')
        return Exhibitor.objects.filter(event_id=event_id).order_by('name')
    
    def get_event(self):
        """
        Get parent event and validate it exists and is active.
        Returns 404 if not found or soft-deleted.
        """
        return get_object_or_404(Event, id=self.kwargs['event_id'], is_active=True)
    
    def perform_create(self, serializer):
        """
        Create Exhibitor linked to parent event.
        """
        serializer.save(event=self.get_event())
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete Exhibitor and return success response.
        """
        instance = self.get_object()
        exhibitor_name = instance.name
        self.perform_destroy(instance)
        
        return Response(
            {
                'success': True,
                'message': f'Exhibitor "{exhibitor_name}" deleted successfully'
            },
            status=status.HTTP_200_OK
        )


# ==================== DEAL VIEWSET ====================

class DealViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Deal management (CRUD operations).
    
    Requires: Authentication (IsAuthenticated)
    
    Supports:
    - Create: POST /events/{event_id}/deals/
    - List: GET /events/{event_id}/deals/
    - Retrieve: GET /events/{event_id}/deals/{id}/
    - Update: PATCH /events/{event_id}/deals/{id}/
    - Delete: DELETE /events/{event_id}/deals/{id}/
    """
    
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get Deals filtered by parent event.
        """
        event_id = self.kwargs.get('event_id')
        return Deal.objects.filter(event_id=event_id).order_by('-expiry_date')
    
    def get_event(self):
        """
        Get parent event and validate it exists and is active.
        Returns 404 if not found or soft-deleted.
        """
        return get_object_or_404(Event, id=self.kwargs['event_id'], is_active=True)
    
    def perform_create(self, serializer):
        """
        Create Deal linked to parent event.
        """
        serializer.save(event=self.get_event())
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete Deal and return success response.
        """
        instance = self.get_object()
        deal_title = instance.title
        self.perform_destroy(instance)
        
        return Response(
            {
                'success': True,
                'message': f'Deal "{deal_title}" deleted successfully'
            },
            status=status.HTTP_200_OK
        )
