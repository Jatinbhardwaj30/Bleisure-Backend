from django.urls import path
from .views import (
    OnboardingAPIView,
    UserProfileRetrieveAPIView,
    UserProfileUpdateAPIView,
    CheckOnboardingStatusAPIView,
    ConferenceListCreateAPIView,
    ConferenceRetrieveUpdateDestroyAPIView,
    ConferenceMarkInterestedAPIView,
    ConferenceRateAPIView
)

app_name = 'bleisure'

urlpatterns = [
    # ============ User Onboarding Endpoints ============
    path('onboarding/', OnboardingAPIView.as_view(), name='onboarding'),
    path('onboarding-status/', CheckOnboardingStatusAPIView.as_view(), name='onboarding_status'),
    
    # ============ User Profile Endpoints ============
    path('profile/', UserProfileRetrieveAPIView.as_view(), name='profile_retrieve'),
    path('profile/update/', UserProfileUpdateAPIView.as_view(), name='profile_update'),
    
    # ============ Conference Endpoints ============
    path('conferences/', ConferenceListCreateAPIView.as_view(), name='conference_list_create'),
    path('conferences/<int:id>/', ConferenceRetrieveUpdateDestroyAPIView.as_view(), name='conference_detail'),
    path('conferences/<int:id>/mark-interested/', ConferenceMarkInterestedAPIView.as_view(), name='conference_mark_interested'),
    path('conferences/<int:id>/rate/', ConferenceRateAPIView.as_view(), name='conference_rate'),
]
