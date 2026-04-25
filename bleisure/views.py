from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django.db.models import Q

from .models import UserProfile, Event, SubEvent, UserEventInterest, UserEventReview
from .serializers import (
    UserProfileSerializer,
    UserProfileCreateUpdateSerializer,
    ProfileDetailSerializer,
    OnboardingResponseSerializer,
    EventCreateSerializer,
    EventListSerializer,
    EventDetailSerializer,
    EventUpdateSerializer,
    SubEventSerializer
)
from .pagination import EventCursorPagination
from core.exceptions import CustomApiException


class OnboardingAPIView(APIView):
    """
    API endpoint for user onboarding.
    Handles both creation and update of user profiles.
    
    POST /api/bleisure/onboarding/
    - If profile exists → update
    - Else → create
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Create or update user profile during onboarding.
        
        Request body:
        {
            "role": "UI Designer",
            "industry": "Design",
            "interest": "Product Design",
            "budget": 200000,
            "location_city": "Mumbai",
            "location_country": "India",
            "linkedin_text": "I am a designer..."
        }
        """
        try:
            user = request.user
            
            # Check if profile exists
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Serialize the data
            serializer = UserProfileCreateUpdateSerializer(
                profile,
                data=request.data,
                context={'request': request},
                partial=False
            )
            
            if serializer.is_valid():
                serializer.save()
                
                action = "created" if created else "updated"
                return Response(
                    {
                        'success': True,
                        'message': f'Profile {action} successfully',
                        'data': ProfileDetailSerializer(profile).data
                    },
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
            
            return Response(
                {
                    'success': False,
                    'message': 'Validation errors occurred',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': str(e)
                }
            )


class UserProfileRetrieveAPIView(APIView):
    """
    API endpoint to retrieve user profile.
    
    GET /api/bleisure/profile/
    - Returns user's complete profile information
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get user profile details.
        """
        try:
            user = request.user
            
            # Retrieve profile with select_related optimization
            profile = UserProfile.objects.select_related('user').get(user=user)
            
            serializer = ProfileDetailSerializer(profile)
            
            return Response(
                {
                    'success': True,
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Profile not found. Please complete onboarding first.',
                    'data': None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': str(e)
                }
            )


class UserProfileUpdateAPIView(APIView):
    """
    API endpoint to update user profile.
    
    PATCH /api/bleisure/profile/
    - Allows partial update of profile
    - All fields are optional
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        """
        Partially update user profile.
        
        Request body:
        {
            "role": "Product Manager",  # Optional
            "budget": 500000,           # Optional
            ...
        }
        """
        try:
            user = request.user
            
            # Retrieve profile
            profile = get_object_or_404(UserProfile, user=user)
            
            # Serialize the data (partial=True allows partial updates)
            serializer = UserProfileCreateUpdateSerializer(
                profile,
                data=request.data,
                context={'request': request},
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                
                return Response(
                    {
                        'success': True,
                        'message': 'Profile updated successfully',
                        'data': ProfileDetailSerializer(profile).data
                    },
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {
                    'success': False,
                    'message': 'Validation errors occurred',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Profile not found. Please complete onboarding first.',
                    'data': None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': str(e)
                }
            )


class CheckOnboardingStatusAPIView(APIView):
    """
    API endpoint to check onboarding status.
    
    GET /api/bleisure/onboarding-status/
    - Returns whether user has completed onboarding
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Check if user has completed onboarding.
        """
        try:
            user = request.user
            
            # Check if profile exists
            profile_exists = UserProfile.objects.filter(user=user).exists()
            
            if profile_exists:
                profile = UserProfile.objects.select_related('user').get(user=user)
                return Response(
                    {
                        'success': True,
                        'onboarded': True,
                        'message': 'User has completed onboarding',
                        'data': ProfileDetailSerializer(profile).data
                    },
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {
                    'success': True,
                    'onboarded': False,
                    'message': 'User has not completed onboarding',
                    'data': None
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': str(e)
                }
            )


# ==================== EVENT VIEWS ====================


class EventFilter(filters.FilterSet):
    """
    Custom filterset for Event model.
    Supports filtering by city, country, type, category, and date ranges.
    """
    
    city = filters.CharFilter(
        field_name='city',
        lookup_expr='icontains',
        help_text='Filter by city (case-insensitive)'
    )
    
    country = filters.CharFilter(
        field_name='country',
        lookup_expr='icontains',
        help_text='Filter by country (case-insensitive)'
    )
    
    type = filters.CharFilter(
        field_name='type',
        help_text='Filter by event type'
    )
    
    category = filters.CharFilter(
        field_name='category',
        lookup_expr='icontains',
        help_text='Filter by category (case-insensitive)'
    )
    
    start_date_from = filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        help_text='Filter events starting from this date'
    )
    
    start_date_to = filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        help_text='Filter events starting until this date'
    )
    
    end_date_from = filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte',
        help_text='Filter events ending from this date'
    )
    
    end_date_to = filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        help_text='Filter events ending until this date'
    )
    
    search = filters.CharFilter(
        method='filter_search',
        help_text='Search by title or description'
    )
    
    tags = filters.CharFilter(
        method='filter_tags',
        help_text='Filter by tags (JSON array)'
    )
    
    class Meta:
        model = Event
        fields = []
    
    def filter_search(self, queryset, name, value):
        """Search across title and description fields."""
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset
    
    def filter_tags(self, queryset, name, value):
        """Filter by tags contained in JSONField using optimized JSONField query."""
        if value:
            # Support comma-separated tag values
            tag_list = [t.strip() for t in value.split(',')]
            # Use overlap for multiple tags (more efficient for JSONField queries)
            # Note: overlap operator works best with PostgreSQL; for SQLite fallback to contains
            queryset = queryset.filter(tags__overlap=tag_list)
        return queryset


class EventListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating events.
    
    GET /api/bleisure/events/
    - List all active events with cursor-based pagination
    - Supports filtering by city, country, type, category, dates
    - Supports searching by title or description
    
    POST /api/bleisure/events/
    - Create a new event
    - Prevents duplicates using source_url
    - Requires authentication
    """
    
    queryset = Event.objects.filter(is_active=True)
    pagination_class = EventCursorPagination
    filterset_class = EventFilter
    filter_backends = (filters.DjangoFilterBackend,)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return EventCreateSerializer
        return EventListSerializer
    
    def get_permissions(self):
        """
        POST requires authentication, GET is public.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []
    
    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related.
        Apply filters and ordering.
        """
        queryset = super().get_queryset()
        
        # Only return active events
        queryset = queryset.filter(is_active=True)
        
        # Optimize database queries
        queryset = queryset.only(
            'id', 'title', 'slug', 'city', 'country', 'venue',
            'start_date', 'end_date', 'timezone', 'type', 'category',
            'price_min', 'price_max', 'currency', 'is_free', 'banner_image',
            'rating', 'interested_count', 'source', 'is_featured', 'created_at', 'is_active'
        )
        
        # Apply ordering
        queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List events with pagination and filtering.
        """
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': f'Error listing events: {str(e)}'
                }
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new event.
        Prevents duplicates using source_url.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(
                {
                    'success': True,
                    'message': 'Event created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': str(e),
                    'errors': serializer.errors if 'serializer' in locals() else {}
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class EventRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting events.
    
    GET /api/bleisure/events/{id}/
    - Retrieve event details
    
    PATCH /api/bleisure/events/{id}/
    - Update event (partial update allowed)
    - Requires authentication
    
    DELETE /api/bleisure/events/{id}/
    - (Soft) Delete event by marking is_active=False
    - Requires authentication
    """
    
    queryset = Event.objects.filter(is_active=True)
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return EventDetailSerializer
        return EventUpdateSerializer
    
    def get_permissions(self):
        """
        GET is public, PATCH/DELETE require authentication.
        """
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve event details."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    'success': True,
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Event.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Event not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def update(self, request, *args, **kwargs):
        """Update event details."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                {
                    'success': True,
                    'message': 'Event updated successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Event.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Event not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete event by marking as inactive."""
        try:
            instance = self.get_object()
            instance.is_active = False
            instance.save()
            
            return Response(
                {
                    'success': True,
                    'message': 'Event deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Event.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Event not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class SubEventListAPIView(generics.ListAPIView):
    """
    API endpoint for listing sub-events within an event.
    
    GET /api/bleisure/events/{event_id}/sub-events/
    - List all sub-events for a specific event
    - Supports filtering by type: ?type=agenda or ?type=side_event
    """
    
    serializer_class = SubEventSerializer
    permission_classes = []
    
    def get_queryset(self):
        """
        Filter sub-events by event_id and optional type parameter.
        Validates that the parent event exists and is active.
        """
        event_id = self.kwargs.get('event_id')
        
        # Validate parent event exists and is active
        get_object_or_404(Event, id=event_id, is_active=True)
        
        queryset = SubEvent.objects.filter(event_id=event_id).order_by('start_time')
        
        # Filter by type if provided
        type_param = self.request.query_params.get('type')
        if type_param:
            queryset = queryset.filter(type=type_param)
        
        return queryset


class EventMarkInterestedAPIView(APIView):
    """
    API endpoint to mark user as interested in an event.
    Tracks interest in UserEventInterest model and prevents duplicate markings.
    
    POST /api/bleisure/events/{id}/mark-interested/
    - Requires authentication
    - Only authenticated users can mark interest
    - Prevents duplicate interest markings
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        """
        Mark user as interested in event.
        If already interested, returns 200 with already_marked=True.
        """
        try:
            event = Event.objects.get(id=id, is_active=True)
            user = request.user
            
            # Try to create or get the interest record
            interest, created = UserEventInterest.objects.get_or_create(
                user=user,
                event=event
            )
            
            # Metrics updated via signal handlers (post_save)
            
            if created:
                return Response(
                    {
                        'success': True,
                        'message': 'Interest marked successfully',
                        'already_marked': False,
                        'interested_count': event.interested_count
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Already marked interest
                return Response(
                    {
                        'success': True,
                        'message': 'You have already marked interest in this event',
                        'already_marked': True,
                        'interested_count': event.interested_count
                    },
                    status=status.HTTP_200_OK
                )
        
        except Event.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Event not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': str(e)
                }
            )


class EventReviewAPIView(APIView):
    """
    API endpoint to review/rate an event.
    Tracks reviews in UserEventReview model.
    Automatically calculates and updates aggregated rating.
    
    POST /api/bleisure/events/{id}/review/
    - Requires authentication
    - Rating must be between 0-5
    - One review per user per event (updates if already reviewed)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        """
        Review/rate an event.
        
        Request body:
        {
            "rating": 4.5  # Must be 0-5
        }
        
        Returns:
        - 200: Review created/updated successfully
        - 400: Invalid rating value
        - 404: Event not found
        """
        try:
            rating = request.data.get('rating')
            
            # Validate rating
            if rating is None:
                return Response(
                    {
                        'success': False,
                        'message': 'Rating is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                return Response(
                    {
                        'success': False,
                        'message': 'Rating must be a number'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if rating < 0 or rating > 5:
                return Response(
                    {
                        'success': False,
                        'message': 'Rating must be between 0 and 5'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            event = Event.objects.get(id=id, is_active=True)
            user = request.user
            
            # Extract optional review text
            review_text = request.data.get('review_text')
            
            # Create or update user's review for this event
            user_review, created = UserEventReview.objects.update_or_create(
                user=user,
                event=event,
                defaults={
                    'rating': rating,
                    'review_text': review_text
                }
            )
            
            # Metrics updated via signal handlers (post_save)
            
            action = "submitted" if created else "updated"
            return Response(
                {
                    'success': True,
                    'message': f'Review {action} successfully',
                    'your_rating': user_review.rating,
                    'average_rating': event.rating,
                    'total_reviews': event.user_reviews.count()
                },
                status=status.HTTP_200_OK
            )
        
        except Event.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Event not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': str(e)
                }
            )
