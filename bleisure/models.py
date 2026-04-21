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


class Conference(models.Model):
    """
    Conference model for conference platform.
    Stores information about conferences with slug generation and deduplication.
    """
    
    # Primary and identifiers
    title = models.CharField(
        max_length=255,
        help_text="Conference title"
    )
    
    slug = models.SlugField(
        unique=True,
        max_length=255,
        help_text="URL-friendly slug auto-generated from title"
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed description of the conference"
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
        help_text="City where conference is held"
    )
    
    country = models.CharField(
        max_length=100,
        help_text="Country where conference is held"
    )
    
    venue = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Venue/location details"
    )
    
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="Timezone of the conference"
    )
    
    # Engagement metrics
    rating = models.FloatField(
        default=0.0,
        help_text="Conference rating (0-5)"
    )
    
    interested_count = models.IntegerField(
        default=0,
        help_text="Number of users interested in this conference"
    )
    
    # Source and deduplication
    source = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Source of conference information (e.g., 'EventBrite', 'LinkedIn')"
    )
    
    source_url = models.URLField(
        unique=True,
        max_length=500,
        null=True,
        blank=True,
        help_text="URL of the conference source"
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
        help_text="Whether this conference is active/visible"
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
        db_table = 'bleisure_conference'
        verbose_name = 'Conference'
        verbose_name_plural = 'Conferences'
        ordering = ['-created_at']
        
        # Database indexes for common queries
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['city']),
            models.Index(fields=['start_date']),
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
            while Conference.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        # Generate hash for deduplication if not provided
        if not self.hash and self.source_url:
            hash_input = f"{self.source_url}{self.title}{self.start_date}"
            self.hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        super().save(*args, **kwargs)
    
    def get_average_rating(self):
        """Calculate average rating from all user ratings."""
        from django.db.models import Avg
        avg = self.user_ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else 0.0
    
    def get_interested_count(self):
        """Get actual interested count from UserConferenceInterest records."""
        return self.interested_users.count()
    
    def update_metrics(self):
        """Update rating and interested_count fields based on related records."""
        self.rating = self.get_average_rating()
        self.interested_count = self.get_interested_count()
        self.save(update_fields=['rating', 'interested_count'])

    def __str__(self):
        return f"{self.title} ({self.city}, {self.country})"


class UserConferenceInterest(models.Model):
    """
    Track user interest in conferences.
    Prevents duplicate interest markings and enables user-conference relationship tracking.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='conference_interests',
        help_text="User who marked interest"
    )
    
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='interested_users',
        help_text="Conference the user is interested in"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user marked interest"
    )
    
    class Meta:
        db_table = 'bleisure_user_conference_interest'
        verbose_name = 'User Conference Interest'
        verbose_name_plural = 'User Conference Interests'
        unique_together = [['user', 'conference']]  # Prevent duplicate interests
        ordering = ['-created_at']
        
        # Database indexes
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['conference']),
            models.Index(fields=['user', 'conference']),
        ]
    
    def __str__(self):
        return f"{self.user.email} interested in {self.conference.title}"


class UserConferenceRating(models.Model):
    """
    Track user ratings for conferences.
    Allows multiple ratings per conference from different users.
    Enables rating aggregation for display_rating calculation.
    """
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='conference_ratings',
        help_text="User who submitted the rating"
    )
    
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='user_ratings',
        help_text="Conference being rated"
    )
    
    rating = models.FloatField(
        help_text="Rating value (0-5 stars)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When rating was submitted"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When rating was last updated"
    )
    
    class Meta:
        db_table = 'bleisure_user_conference_rating'
        verbose_name = 'User Conference Rating'
        verbose_name_plural = 'User Conference Ratings'
        unique_together = [['user', 'conference']]  # One rating per user per conference
        ordering = ['-created_at']
        
        # Database indexes
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['conference']),
            models.Index(fields=['user', 'conference']),
        ]
    
    def __str__(self):
        return f"{self.user.email} rated {self.conference.title}: {self.rating}/5"
