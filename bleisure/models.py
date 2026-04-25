from django.db import models
from django.utils.text import slugify
from users.models import CustomUser
import hashlib


class UserProfile(models.Model):
    """
    Extended user profile with onboarding information.
    One-to-one relationship with CustomUser.
    """
    
    ROLE_CHOICES = [
        ('UI Designer', 'UI Designer'),
        ('UX Designer', 'UX Designer'),
        ('Product Manager', 'Product Manager'),
        ('Developer', 'Developer'),
        ('Business Analyst', 'Business Analyst'),
        ('Marketing', 'Marketing'),
        ('Sales', 'Sales'),
        ('Executive', 'Executive'),
        ('Other', 'Other'),
    ]
    
    INDUSTRY_CHOICES = [
        ('Design', 'Design'),
        ('Technology', 'Technology'),
        ('Finance', 'Finance'),
        ('Healthcare', 'Healthcare'),
        ('Retail', 'Retail'),
        ('Manufacturing', 'Manufacturing'),
        ('Education', 'Education'),
        ('Entertainment', 'Entertainment'),
        ('Hospitality', 'Hospitality'),
        ('Other', 'Other'),
    ]
    
    # Core relationship
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Profile fields
    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        null=True,
        blank=True,
        help_text="User's professional role"
    )
    
    industry = models.CharField(
        max_length=100,
        choices=INDUSTRY_CHOICES,
        null=True,
        blank=True,
        help_text="Industry user works in"
    )
    
    interest = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="User's primary interest"
    )
    
    budget = models.FloatField(
        null=True,
        blank=True,
        help_text="Budget in currency"
    )
    
    location_city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="City where user is located"
    )
    
    location_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Country where user is located"
    )
    
    linkedin_text = models.TextField(
        null=True,
        blank=True,
        help_text="LinkedIn bio or professional summary"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bleisure_user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Profile of {self.user.email} - {self.user.full_name}"


class Event(models.Model):
    """
    Event model for events platform.
    Stores information about events (conferences, workshops, webinars, meetups) with slug generation and deduplication.
    """
    
    EVENT_TYPE_CHOICES = [
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('webinar', 'Webinar'),
        ('meetup', 'Meetup'),
    ]
    
    # Primary and identifiers
    title = models.CharField(
        max_length=255,
        help_text="Event title"
    )
    
    slug = models.SlugField(
        unique=True,
        max_length=255,
        help_text="URL-friendly slug auto-generated from title"
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed description of the event"
    )
    
    type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default='conference',
        help_text="Type of event"
    )
    
    category = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Category of event"
    )
    
    tags = models.JSONField(
        null=True,
        blank=True,
        help_text="Tags for event organization"
    )
    
    # Date and time information
    start_date = models.DateField(
        help_text="Conference start date"
    )
    
    end_date = models.DateField(
        help_text="Conference end date"
    )
    
    # Location information
    city = models.CharField(
        max_length=100,
        db_index=True,
        help_text="City where event is held"
    )
    
    country = models.CharField(
        max_length=100,
        help_text="Country where event is held"
    )
    
    venue = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Venue/location details"
    )
    
    address = models.TextField(
        null=True,
        blank=True,
        help_text="Full address of the event"
    )
    
    latitude = models.FloatField(
        null=True,
        blank=True,
        help_text="Latitude coordinate"
    )
    
    longitude = models.FloatField(
        null=True,
        blank=True,
        help_text="Longitude coordinate"
    )
    
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="Timezone of the event"
    )
    
    # Organizer information
    organizer_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Name of event organizer"
    )
    
    # Pricing information
    price_min = models.FloatField(
        null=True,
        blank=True,
        help_text="Minimum ticket price"
    )
    
    price_max = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum ticket price"
    )
    
    currency = models.CharField(
        max_length=10,
        default='INR',
        help_text="Currency for pricing"
    )
    
    is_free = models.BooleanField(
        default=False,
        help_text="Whether the event is free"
    )
    
    # Media
    banner_image = models.URLField(
        null=True,
        blank=True,
        help_text="URL of banner image"
    )
    
    # URLs
    website_url = models.URLField(
        null=True,
        blank=True,
        help_text="Official website URL"
    )
    
    registration_url = models.URLField(
        null=True,
        blank=True,
        help_text="Registration/ticket URL"
    )
    
    # Featured flag
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether the event is featured"
    )
    
    # Engagement metrics
    rating = models.FloatField(
        default=0.0,
        help_text="Event rating (0-5)"
    )
    
    interested_count = models.IntegerField(
        default=0,
        help_text="Number of users interested in this event"
    )
    
    # Source and deduplication
    source = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Source of event information (e.g., 'EventBrite', 'LinkedIn')"
    )
    
    source_url = models.URLField(
        unique=True,
        max_length=500,
        null=True,
        blank=True,
        help_text="URL of the event source"
    )
    
    hash = models.CharField(
        unique=True,
        max_length=64,
        null=True,
        blank=True,
        help_text="Hash for deduplication"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this event is active/visible"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Created timestamp"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last updated timestamp"
    )
    
    class Meta:
        db_table = 'bleisure_event'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-created_at']
        
        # Database indexes for common queries
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['city']),
            models.Index(fields=['type']),
            models.Index(fields=['start_date']),
            models.Index(fields=['source_url']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['city', 'start_date']),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate slug and hash."""
        # Auto-generate slug from title
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Ensure slug uniqueness
            while Event.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        # Generate hash for deduplication if not provided
        if not self.hash and self.source_url:
            hash_input = f"{self.source_url}{self.title}{self.start_date}"
            self.hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        super().save(*args, **kwargs)
    
    def get_average_rating(self):
        """Calculate average rating from all user reviews."""
        from django.db.models import Avg
        avg = self.user_reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else 0.0
    
    def get_interested_count(self):
        """Get actual interested count from UserEventInterest records."""
        return self.interested_users.count()
    
    def update_metrics(self):
        """Update rating and interested_count fields based on related records."""
        self.rating = self.get_average_rating()
        self.interested_count = self.get_interested_count()
        self.save(update_fields=['rating', 'interested_count'])

    def __str__(self):
        return f"{self.title} ({self.city}, {self.country})"


class SubEvent(models.Model):
    """
    SubEvent model for sub-events within an Event.
    Represents agendas or side events within a parent event.
    """
    
    TYPE_CHOICES = [
        ('agenda', 'Agenda'),
        ('side_event', 'Side Event')
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='sub_events',
        help_text="Parent event"
    )
    
    title = models.CharField(
        max_length=255,
        help_text="SubEvent title"
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="Type of sub-event"
    )
    
    start_time = models.DateTimeField(
        help_text="Start time of sub-event"
    )
    
    end_time = models.DateTimeField(
        help_text="End time of sub-event"
    )
    
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Location within venue"
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Description of sub-event"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bleisure_sub_event'
        verbose_name = 'Sub Event'
        verbose_name_plural = 'Sub Events'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['start_time']),
            models.Index(fields=['event', 'type']),  # Composite index for filtering by event and type
        ]
    
    def __str__(self):
        return f"{self.title} ({self.event.title})"


class UserEventInterest(models.Model):
    """
    Track user interest in events.
    Prevents duplicate interest markings and enables user-event relationship tracking.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='event_interests',
        help_text="User who marked interest"
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='interested_users',
        help_text="Event the user is interested in"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user marked interest"
    )
    
    class Meta:
        db_table = 'bleisure_user_event_interest'
        verbose_name = 'User Event Interest'
        verbose_name_plural = 'User Event Interests'
        unique_together = [['user', 'event']]  # Prevent duplicate interests
        ordering = ['-created_at']
        
        # Database indexes
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['event']),
            models.Index(fields=['user', 'event']),
        ]
    
    def __str__(self):
        return f"{self.user.email} interested in {self.event.title}"


class UserEventReview(models.Model):
    """
    Track user reviews/ratings for events.
    Allows multiple reviews per event from different users.
    Enables rating aggregation for display_rating calculation.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='event_reviews',
        help_text="User who submitted the review"
    )
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='user_reviews',
        help_text="Event being reviewed"
    )
    
    rating = models.FloatField(
        help_text="Rating value (0-5 stars)"
    )
    
    review_text = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed review text"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When review was submitted"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When review was last updated"
    )
    
    class Meta:
        db_table = 'bleisure_user_event_review'
        verbose_name = 'User Event Review'
        verbose_name_plural = 'User Event Reviews'
        unique_together = [['user', 'event']]  # One review per user per event
        ordering = ['-created_at']
        
        # Database indexes
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['event']),
            models.Index(fields=['user', 'event']),
        ]
    
    def __str__(self):
        return f"{self.user.email} reviewed {self.event.title}: {self.rating}/5"


class Speaker(models.Model):
    """
    Speaker model for event speakers.
    Tracks speakers participating in events.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='speakers',
        help_text="Event where speaker is presenting"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Speaker's full name"
    )
    
    company = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Company the speaker works at"
    )
    
    designation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Speaker's job title/designation"
    )
    
    bio = models.TextField(
        null=True,
        blank=True,
        help_text="Speaker biography"
    )
    
    profile_image = models.URLField(
        null=True,
        blank=True,
        help_text="Speaker's profile image URL"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bleisure_speaker'
        verbose_name = 'Speaker'
        verbose_name_plural = 'Speakers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.event.title})"


class Exhibitor(models.Model):
    """
    Exhibitor model for event exhibitors/sponsors.
    Tracks companies exhibiting at events.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='exhibitors',
        help_text="Event where exhibitor is participating"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Exhibitor/company name"
    )
    
    website = models.URLField(
        null=True,
        blank=True,
        help_text="Exhibitor website URL"
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Company/exhibitor description"
    )
    
    booth_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Booth number at event"
    )
    
    logo = models.URLField(
        null=True,
        blank=True,
        help_text="Exhibitor logo URL"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bleisure_exhibitor'
        verbose_name = 'Exhibitor'
        verbose_name_plural = 'Exhibitors'
        ordering = ['name']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.event.title})"


class Deal(models.Model):
    """
    Deal model for event-specific deals and offers.
    Tracks special offers associated with events.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='deals',
        help_text="Event associated with this deal"
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Deal title"
    )
    
    description = models.TextField(
        help_text="Deal description"
    )
    
    discount_percentage = models.FloatField(
        null=True,
        blank=True,
        help_text="Discount percentage (0-100)"
    )
    
    discount_amount = models.FloatField(
        null=True,
        blank=True,
        help_text="Fixed discount amount"
    )
    
    code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Discount/promo code"
    )
    
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Deal expiry date"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the deal is active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bleisure_deal'
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.event.title})"
