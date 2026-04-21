from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django.db.models import Q

from .models import UserProfile, Conference, UserConferenceInterest, UserConferenceRating
from .serializers import (
    UserProfileSerializer,
    UserProfileCreateUpdateSerializer,
    ProfileDetailSerializer,
    OnboardingResponseSerializer,
    ConferenceCreateSerializer,
    ConferenceListSerializer,
    ConferenceDetailSerializer,
    ConferenceUpdateSerializer
)
from .pagination import ConferenceCursorPagination
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


# ==================== CONFERENCE VIEWS ====================


class ConferenceFilter(filters.FilterSet):
    """
    Custom filterset for Conference model.
    Supports filtering by city, country, and date ranges.
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
    
    start_date_from = filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        help_text='Filter conferences starting from this date'
    )
    
    start_date_to = filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        help_text='Filter conferences starting until this date'
    )
    
    end_date_from = filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte',
        help_text='Filter conferences ending from this date'
    )
    
    end_date_to = filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        help_text='Filter conferences ending until this date'
    )
    
    search = filters.CharFilter(
        method='filter_search',
        help_text='Search by title or description'
    )
    
    class Meta:
        model = Conference
        fields = []
    
    def filter_search(self, queryset, name, value):
        """Search across title and description fields."""
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset


class ConferenceListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating conferences.
    
    GET /api/bleisure/conferences/
    - List all active conferences with cursor-based pagination
    - Supports filtering by city, country, dates
    - Supports searching by title or description
    
    POST /api/bleisure/conferences/
    - Create a new conference
    - Prevents duplicates using source_url
    - Requires authentication
    """
    
    queryset = Conference.objects.filter(is_active=True)
    pagination_class = ConferenceCursorPagination
    filterset_class = ConferenceFilter
    filter_backends = (filters.DjangoFilterBackend,)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return ConferenceCreateSerializer
        return ConferenceListSerializer
    
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
        
        # Only return active conferences
        queryset = queryset.filter(is_active=True)
        
        # Optimize database queries
        queryset = queryset.only(
            'id', 'title', 'slug', 'city', 'country', 'venue',
            'start_date', 'end_date', 'timezone', 'rating',
            'interested_count', 'source', 'created_at', 'is_active'
        )
        
        # Apply ordering
        queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List conferences with pagination and filtering.
        """
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            raise CustomApiException(
                500,
                {
                    'success': False,
                    'message': f'Error listing conferences: {str(e)}'
                }
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conference.
        Prevents duplicates using source_url.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(
                {
                    'success': True,
                    'message': 'Conference created successfully',
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


class ConferenceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting conferences.
    
    GET /api/bleisure/conferences/{id}/
    - Retrieve conference details
    
    PATCH /api/bleisure/conferences/{id}/
    - Update conference (partial update allowed)
    - Requires authentication
    
    DELETE /api/bleisure/conferences/{id}/
    - (Soft) Delete conference by marking is_active=False
    - Requires authentication
    """
    
    queryset = Conference.objects.filter(is_active=True)
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return ConferenceDetailSerializer
        return ConferenceUpdateSerializer
    
    def get_permissions(self):
        """
        GET is public, PATCH/DELETE require authentication.
        """
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve conference details."""
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
        except Conference.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Conference not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def update(self, request, *args, **kwargs):
        """Update conference details."""
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
                    'message': 'Conference updated successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Conference.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Conference not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete conference by marking as inactive."""
        try:
            instance = self.get_object()
            instance.is_active = False
            instance.save()
            
            return Response(
                {
                    'success': True,
                    'message': 'Conference deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Conference.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Conference not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ConferenceMarkInterestedAPIView(APIView):
    """
    API endpoint to mark user as interested in a conference.
    Tracks interest in UserConferenceInterest model and prevents duplicate markings.
    
    POST /api/bleisure/conferences/{id}/mark-interested/
    - Requires authentication
    - Only authenticated users can mark interest
    - Prevents duplicate interest markings
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        """
        Mark user as interested in conference.
        If already interested, returns 200 with already_marked=True.
        """
        try:
            conference = Conference.objects.get(id=id, is_active=True)
            user = request.user
            
            # Try to create or get the interest record
            interest, created = UserConferenceInterest.objects.get_or_create(
                user=user,
                conference=conference
            )
            
            # Update metrics
            conference.update_metrics()
            
            if created:
                return Response(
                    {
                        'success': True,
                        'message': 'Interest marked successfully',
                        'already_marked': False,
                        'interested_count': conference.interested_count
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Already marked interest
                return Response(
                    {
                        'success': True,
                        'message': 'You have already marked interest in this conference',
                        'already_marked': True,
                        'interested_count': conference.interested_count
                    },
                    status=status.HTTP_200_OK
                )
        
        except Conference.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Conference not found'
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


class ConferenceRateAPIView(APIView):
    """
    API endpoint to rate a conference.
    Tracks ratings in UserConferenceRating model.
    Automatically calculates and updates aggregated rating.
    
    POST /api/bleisure/conferences/{id}/rate/
    - Requires authentication
    - Rating must be between 0-5
    - One rating per user per conference (updates if already rated)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        """
        Rate a conference.
        
        Request body:
        {
            "rating": 4.5  # Must be 0-5
        }
        
        Returns:
        - 200: Rating created/updated successfully
        - 400: Invalid rating value
        - 404: Conference not found
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
            
            conference = Conference.objects.get(id=id, is_active=True)
            user = request.user
            
            # Create or update user's rating for this conference
            user_rating, created = UserConferenceRating.objects.update_or_create(
                user=user,
                conference=conference,
                defaults={'rating': rating}
            )
            
            # Update conference's aggregated rating
            conference.update_metrics()
            
            action = "submitted" if created else "updated"
            return Response(
                {
                    'success': True,
                    'message': f'Rating {action} successfully',
                    'your_rating': user_rating.rating,
                    'average_rating': conference.rating,
                    'total_ratings': conference.user_ratings.count()
                },
                status=status.HTTP_200_OK
            )
        
        except Conference.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Conference not found'
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
