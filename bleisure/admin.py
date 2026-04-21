from django.contrib import admin
from .models import UserProfile, Conference, UserConferenceInterest, UserConferenceRating


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


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Conference model.
    """
    list_display = (
        'id',
        'title',
        'city',
        'country',
        'start_date',
        'end_date',
        'rating',
        'interested_count',
        'is_active',
        'created_at'
    )
    
    list_display_links = ('id', 'title')  # Make both id and title clickable
    
    list_filter = (
        'is_active',
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
        'venue'
    )
    
    readonly_fields = (
        'slug',
        'hash',
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Dates & Time', {
            'fields': ('start_date', 'end_date', 'timezone')
        }),
        ('Location', {
            'fields': ('city', 'country', 'venue')
        }),
        ('Engagement', {
            'fields': ('rating', 'interested_count')
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


@admin.register(UserConferenceInterest)
class UserConferenceInterestAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserConferenceInterest model.
    Tracks user interest in conferences.
    """
    list_display = (
        'id',
        'user',
        'conference',
        'created_at'
    )
    
    list_filter = (
        'created_at',
        'user',
        'conference'
    )
    
    search_fields = (
        'user__email',
        'user__full_name',
        'conference__title',
        'conference__city'
    )
    
    readonly_fields = ('created_at', 'user', 'conference')
    
    fieldsets = (
        ('Interest Record', {
            'fields': ('user', 'conference')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(UserConferenceRating)
class UserConferenceRatingAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserConferenceRating model.
    Tracks ratings submitted by users for conferences.
    """
    list_display = (
        'id',
        'user',
        'conference',
        'rating',
        'created_at',
        'updated_at'
    )
    
    list_filter = (
        'rating',
        'created_at',
        'updated_at',
        'user',
        'conference'
    )
    
    search_fields = (
        'user__email',
        'user__full_name',
        'conference__title',
        'conference__city'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'user', 'conference')
    
    fieldsets = (
        ('Rating Information', {
            'fields': ('user', 'conference', 'rating')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
