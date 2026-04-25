from django.contrib import admin
from .models import UserProfile, Event, SubEvent, UserEventInterest, UserEventReview, Speaker, Exhibitor, Deal


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.
    """
    list_display = (
        'id',
        'user',
        'role',
        'industry',
        'location_city',
        'location_country',
        'created_at'
    )
    
    list_filter = (
        'role',
        'industry',
        'location_country',
        'created_at',
        'updated_at'
    )
    
    search_fields = (
        'user__email',
        'user__full_name',
        'location_city',
        'location_country',
        'interest'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'user')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Details', {
            'fields': ('role', 'industry', 'interest')
        }),
        ('Budget & Location', {
            'fields': ('budget', 'location_city', 'location_country')
        }),
        ('LinkedIn', {
            'fields': ('linkedin_text',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin configuration for Event model.
    """
    list_display = (
        'id',
        'title',
        'type',
        'city',
        'country',
        'start_date',
        'end_date',
        'rating',
        'interested_count',
        'is_featured',
        'is_active',
        'created_at'
    )
    
    list_display_links = ('id', 'title')  # Make both id and title clickable
    
    list_filter = (
        'is_active',
        'is_featured',
        'type',
        'category',
        'city',
        'country',
        'start_date',
        'created_at',
        'source'
    )
    
    search_fields = (
        'title',
        'description',
        'city',
        'country',
        'venue',
        'organizer_name'
    )
    
    readonly_fields = (
        'slug',
        'hash',
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'type', 'category', 'tags')
        }),
        ('Dates & Time', {
            'fields': ('start_date', 'end_date', 'timezone')
        }),
        ('Location', {
            'fields': ('city', 'country', 'venue', 'address', 'latitude', 'longitude')
        }),
        ('Organizer', {
            'fields': ('organizer_name',)
        }),
        ('Pricing', {
            'fields': ('price_min', 'price_max', 'currency', 'is_free')
        }),
        ('Media & URLs', {
            'fields': ('banner_image', 'website_url', 'registration_url')
        }),
        ('Engagement', {
            'fields': ('rating', 'interested_count', 'is_featured')
        }),
        ('Source & Deduplication', {
            'fields': ('source', 'source_url', 'hash')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(SubEvent)
class SubEventAdmin(admin.ModelAdmin):
    """
    Admin configuration for SubEvent model.
    """
    list_display = (
        'id',
        'title',
        'event',
        'type',
        'start_time',
        'end_time',
        'location',
        'created_at'
    )
    
    list_filter = (
        'type',
        'start_time',
        'created_at',
        'event'
    )
    
    search_fields = (
        'title',
        'description',
        'location',
        'event__title'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event', 'title', 'type')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Details', {
            'fields': ('location', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(UserEventInterest)
class UserEventInterestAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserEventInterest model.
    Tracks user interest in events.
    """
    list_display = (
        'id',
        'user',
        'event',
        'created_at'
    )
    
    list_filter = (
        'created_at',
        'user',
        'event'
    )
    
    search_fields = (
        'user__email',
        'user__full_name',
        'event__title',
        'event__city'
    )
    
    readonly_fields = ('created_at', 'user', 'event')
    
    fieldsets = (
        ('Interest Record', {
            'fields': ('user', 'event')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(UserEventReview)
class UserEventReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserEventReview model.
    Tracks reviews submitted by users for events.
    """
    list_display = (
        'id',
        'user',
        'event',
        'rating',
        'created_at',
        'updated_at'
    )
    
    list_filter = (
        'rating',
        'created_at',
        'updated_at',
        'user',
        'event'
    )
    
    search_fields = (
        'user__email',
        'user__full_name',
        'event__title',
        'event__city'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'user', 'event')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'event', 'rating')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    """
    Admin configuration for Speaker model.
    """
    list_display = (
        'id',
        'name',
        'company',
        'designation',
        'event',
        'created_at'
    )
    
    list_filter = (
        'event',
        'created_at',
        'company'
    )
    
    search_fields = (
        'name',
        'company',
        'designation',
        'event__title'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Speaker Information', {
            'fields': ('event', 'name', 'company', 'designation')
        }),
        ('Details', {
            'fields': ('bio', 'profile_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('name',)


@admin.register(Exhibitor)
class ExhibitorAdmin(admin.ModelAdmin):
    """
    Admin configuration for Exhibitor model.
    """
    list_display = (
        'id',
        'name',
        'event',
        'booth_number',
        'website',
        'created_at'
    )
    
    list_filter = (
        'event',
        'created_at'
    )
    
    search_fields = (
        'name',
        'website',
        'event__title'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Exhibitor Information', {
            'fields': ('event', 'name', 'website', 'booth_number')
        }),
        ('Details', {
            'fields': ('description', 'logo')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('name',)


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """
    Admin configuration for Deal model.
    """
    list_display = (
        'id',
        'title',
        'event',
        'code',
        'discount_percentage',
        'discount_amount',
        'is_active',
        'expiry_date',
        'created_at'
    )
    
    list_filter = (
        'event',
        'is_active',
        'expiry_date',
        'created_at'
    )
    
    search_fields = (
        'title',
        'description',
        'code',
        'event__title'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Deal Information', {
            'fields': ('event', 'title', 'code')
        }),
        ('Pricing', {
            'fields': ('discount_percentage', 'discount_amount')
        }),
        ('Details', {
            'fields': ('description', 'expiry_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
