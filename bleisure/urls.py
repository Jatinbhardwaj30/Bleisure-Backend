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
from .viewsets import SubEventViewSet, SpeakerViewSet, ExhibitorViewSet, DealViewSet

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

# Speaker ViewSet views for nested routing
speaker_list = SpeakerViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

speaker_detail = SpeakerViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'put': 'update',
    'delete': 'destroy'
})

# Exhibitor ViewSet views for nested routing
exhibitor_list = ExhibitorViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

exhibitor_detail = ExhibitorViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'put': 'update',
    'delete': 'destroy'
})

# Deal ViewSet views for nested routing
deal_list = DealViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

deal_detail = DealViewSet.as_view({
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
    
    # ============ Speaker Endpoints (ViewSet - Full CRUD) ============
    path('events/<int:event_id>/speakers/', speaker_list, name='event_speakers'),
    path('events/<int:event_id>/speakers/<int:pk>/', speaker_detail, name='event_speaker_detail'),
    
    # ============ Exhibitor Endpoints (ViewSet - Full CRUD) ============
    path('events/<int:event_id>/exhibitors/', exhibitor_list, name='event_exhibitors'),
    path('events/<int:event_id>/exhibitors/<int:pk>/', exhibitor_detail, name='event_exhibitor_detail'),
    
    # ============ Deal Endpoints (ViewSet - Full CRUD) ============
    path('events/<int:event_id>/deals/', deal_list, name='event_deals'),
    path('events/<int:event_id>/deals/<int:pk>/', deal_detail, name='event_deal_detail'),
    
    # ============ Event Actions ============
    path('events/<int:id>/mark-interested/', EventMarkInterestedAPIView.as_view(), name='event_mark_interested'),
    path('events/<int:id>/review/', EventReviewAPIView.as_view(), name='event_review'),
]
