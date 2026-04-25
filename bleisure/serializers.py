from rest_framework import serializers
from .models import UserProfile, Event, SubEvent, UserEventInterest, UserEventReview, Speaker, Exhibitor, Deal
from users.models import CustomUser
from datetime import date


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading UserProfile data.
    Used for GET requests.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user_email',
            'user_full_name',
            'role',
            'industry',
            'interest',
            'budget',
            'location_city',
            'location_country',
            'linkedin_text',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating UserProfile.
    Used for POST and PATCH requests.
    Includes validation for required fields and data constraints.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'role',
            'industry',
            'interest',
            'budget',
            'location_city',
            'location_country',
            'linkedin_text'
        ]
    
    def validate_role(self, value):
        """Validate role is provided and not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Role is required and cannot be empty.")
        return value
    
    def validate_industry(self, value):
        """Validate industry is provided and not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Industry is required and cannot be empty.")
        return value
    
    def validate_interest(self, value):
        """Validate interest is provided and not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Interest is required and cannot be empty.")
        return value
    
    def validate_location_city(self, value):
        """Validate city is provided and not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("City is required and cannot be empty.")
        return value
    
    def validate_location_country(self, value):
        """Validate country is provided and not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Country is required and cannot be empty.")
        return value
    
    def validate_budget(self, value):
        """Validate budget is >= 0."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Budget cannot be negative.")
        return value
    
    def validate(self, data):
        """
        Perform cross-field validation.
        """
        # For creation (POST), ensure all required fields are present
        if self.instance is None:  # Create operation
            required_fields = ['role', 'industry', 'interest', 'location_city', 'location_country']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f"{field.replace('_', ' ').title()} is required."
                    })
        
        return data
    
    def create(self, validated_data):
        """Create a new UserProfile instance."""
        user = self.context['request'].user
        profile = UserProfile.objects.create(
            user=user,
            **validated_data
        )
        return profile
    
    def update(self, instance, validated_data):
        """Update an existing UserProfile instance."""
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class OnboardingResponseSerializer(serializers.Serializer):
    """
    Serializer for onboarding response.
    """
    success = serializers.BooleanField()
    message = serializers.CharField()


class ProfileDetailSerializer(serializers.ModelSerializer):
    """
    Detailed profile serializer with user information.
    Used for comprehensive profile responses.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user_id',
            'user_email',
            'user_full_name',
            'role',
            'industry',
            'interest',
            'budget',
            'location_city',
            'location_country',
            'linkedin_text',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']


# ==================== EVENT SERIALIZERS ====================


class SubEventSerializer(serializers.ModelSerializer):
    """
    Serializer for SubEvent objects with full CRUD and validation.
    Handles time conflict validation and speaker linking.
    """
    
    speaker_name = serializers.CharField(source='speaker.name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    
    class Meta:
        model = SubEvent
        fields = [
            'id',
            'event',
            'event_title',
            'title',
            'type',
            'start_time',
            'end_time',
            'location',
            'description',
            'speaker',
            'speaker_name',
            'external_url',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'event', 'event_title', 'speaker_name', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate:
        - End time is after start time
        - No time conflicts with other sub-events in same event
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Validate end time is after start time
        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time'
            })
        
        # Validate time conflicts
        event = self.context.get('event')
        if event and start_time and end_time:
            overlapping = SubEvent.objects.filter(
                event=event,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            # Exclude current instance if updating
            if self.instance:
                overlapping = overlapping.exclude(id=self.instance.id)
            
            if overlapping.exists():
                conflicting_titles = ', '.join([e.title for e in overlapping[:3]])
                raise serializers.ValidationError({
                    'start_time': f'Time overlaps with: {conflicting_titles}'
                })
        
        return data


class SpeakerSerializer(serializers.ModelSerializer):
    """
    Serializer for Speaker objects.
    Used for nested speakers within Event details.
    """
    
    class Meta:
        model = Speaker
        fields = [
            'id',
            'name',
            'company',
            'designation',
            'bio',
            'profile_image'
        ]
        read_only_fields = ['id']


class ExhibitorSerializer(serializers.ModelSerializer):
    """
    Serializer for Exhibitor objects.
    Used for nested exhibitors within Event details.
    """
    
    class Meta:
        model = Exhibitor
        fields = [
            'id',
            'name',
            'website',
            'description',
            'booth_number',
            'logo'
        ]
        read_only_fields = ['id']


class DealSerializer(serializers.ModelSerializer):
    """
    Serializer for Deal objects.
    Used for nested deals within Event details.
    """
    
    class Meta:
        model = Deal
        fields = [
            'id',
            'title',
            'description',
            'discount_percentage',
            'discount_amount',
            'code',
            'expiry_date',
            'is_active'
        ]
        read_only_fields = ['id']


class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Event objects.
    Handles validation and prevents duplicates using source_url or hash.
    """
    
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'start_date',
            'end_date',
            'city',
            'country',
            'venue',
            'address',
            'latitude',
            'longitude',
            'timezone',
            'type',
            'category',
            'tags',
            'organizer_name',
            'price_min',
            'price_max',
            'currency',
            'is_free',
            'banner_image',
            'website_url',
            'registration_url',
            'is_featured',
            'source',
            'source_url',
            'is_active'
        ]
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()
    
    def validate_city(self, value):
        """Validate city is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("City is required.")
        return value.strip()
    
    def validate_country(self, value):
        """Validate country is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Country is required.")
        return value.strip()
    
    def validate_start_date(self, value):
        """Validate start date is not in the past."""
        if value < date.today():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Validate end date is after start date
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        # Check for duplicate using source_url
        source_url = data.get('source_url')
        if source_url:
            existing = Event.objects.filter(source_url=source_url).exists()
            if existing:
                raise serializers.ValidationError({
                    'source_url': 'Event with this source URL already exists.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create event instance."""
        event = Event.objects.create(**validated_data)
        return event


class EventListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Event objects.
    Lightweight serializer for list views with pagination.
    """
    
    days_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'slug',
            'city',
            'country',
            'venue',
            'start_date',
            'end_date',
            'days_count',
            'timezone',
            'type',
            'category',
            'price_min',
            'price_max',
            'currency',
            'is_free',
            'rating',
            'interested_count',
            'banner_image',
            'source',
            'is_featured',
            'is_active',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'slug',
            'created_at',
            'rating',
            'interested_count'
        ]
    
    def get_days_count(self, obj):
        """Calculate number of days for the event."""
        delta = obj.end_date - obj.start_date
        return delta.days + 1


class EventDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Event information.
    Used for retrieve operations with nested sub_events, speakers, exhibitors, deals.
    """
    
    days_count = serializers.SerializerMethodField()
    sub_events = SubEventSerializer(many=True, read_only=True)
    speakers = SpeakerSerializer(many=True, read_only=True)
    exhibitors = ExhibitorSerializer(many=True, read_only=True)
    deals = DealSerializer(many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'city',
            'country',
            'venue',
            'address',
            'latitude',
            'longitude',
            'start_date',
            'end_date',
            'days_count',
            'timezone',
            'type',
            'category',
            'tags',
            'organizer_name',
            'price_min',
            'price_max',
            'currency',
            'is_free',
            'banner_image',
            'website_url',
            'registration_url',
            'is_featured',
            'rating',
            'interested_count',
            'sub_events',
            'speakers',
            'exhibitors',
            'deals',
            'source',
            'source_url',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'slug',
            'hash',
            'created_at',
            'updated_at'
        ]
    
    def get_days_count(self, obj):
        """Calculate number of days for the event."""
        delta = obj.end_date - obj.start_date
        return delta.days + 1


class EventUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Event objects.
    Allows partial updates of event information.
    
    Note: rating and interested_count are managed through dedicated endpoints:
    - POST /events/{id}/review/ - to update rating
    - POST /events/{id}/mark-interested/ - to increment interested_count
    """
    
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'start_date',
            'end_date',
            'city',
            'country',
            'venue',
            'address',
            'latitude',
            'longitude',
            'timezone',
            'type',
            'category',
            'tags',
            'organizer_name',
            'price_min',
            'price_max',
            'currency',
            'is_free',
            'banner_image',
            'website_url',
            'registration_url',
            'is_featured',
            'is_active'
        ]
    
    def validate_title(self, value):
        """Validate title if provided."""
        if value and len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value
    
    def validate(self, data):
        """Cross-field validation for updates."""
        instance = self.instance
        
        start_date = data.get('start_date', instance.start_date)
        end_date = data.get('end_date', instance.end_date)
        
        if end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        return data
