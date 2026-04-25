from django.urls import path
from .views import (
    OnboardingAPIView,
    UserProfileRetrieveAPIView,
    UserProfileUpdateAPIView,
    CheckOnboardingStatusAPIView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    SubEventListAPIView,
    EventMarkInterestedAPIView,
    EventReviewAPIView
)

app_name = 'bleisure'

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
    path('events/<int:event_id>/sub-events/', SubEventListAPIView.as_view(), name='event_sub_events'),
    path('events/<int:id>/mark-interested/', EventMarkInterestedAPIView.as_view(), name='event_mark_interested'),
    path('events/<int:id>/review/', EventReviewAPIView.as_view(), name='event_review'),
]
