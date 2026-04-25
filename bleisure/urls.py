from django.urls import path
from .views import (
    OnboardingAPIView,
    UserProfileRetrieveAPIView,
    UserProfileUpdateAPIView,
    CheckOnboardingStatusAPIView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    EventMarkInterestedAPIView,
    EventReviewAPIView
)
from .viewsets import SubEventViewSet

app_name = 'bleisure'

# SubEvent ViewSet views for nested routing
subevent_list = SubEventViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

subevent_detail = SubEventViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    # ============ User Onboarding Endpoints ============
    path('onboarding/', OnboardingAPIView.as_view(), name='onboarding'),
    path('onboarding-status/', CheckOnboardingStatusAPIView.as_view(), name='onboarding_status'),
    
    # ============ User Profile Endpoints ============
    path('profile/', UserProfileRetrieveAPIView.as_view(), name='profile_retrieve'),
    path('profile/update/', UserProfileUpdateAPIView.as_view(), name='profile_update'),
    
    # ============ Event Endpoints ============
    path('events/', EventListCreateAPIView.as_view(), name='event_list_create'),
    path('events/<int:id>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='event_detail'),
    
    # ============ SubEvent Endpoints (ViewSet - Full CRUD) ============
    path('events/<int:event_id>/sub-events/', subevent_list, name='event_sub_events'),
    path('events/<int:event_id>/sub-events/<int:pk>/', subevent_detail, name='event_sub_event_detail'),
    
    # ============ Event Actions ============
    path('events/<int:id>/mark-interested/', EventMarkInterestedAPIView.as_view(), name='event_mark_interested'),
    path('events/<int:id>/review/', EventReviewAPIView.as_view(), name='event_review'),
]
