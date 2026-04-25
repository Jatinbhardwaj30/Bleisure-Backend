# Generated migration for Event model refactoring
# Manually ordered to avoid constraint conflicts

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bleisure', '0003_userconferenceinterest_userconferencerating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Delete dependent models first (they reference Conference)
        migrations.DeleteModel(
            name='UserConferenceRating',
        ),
        migrations.DeleteModel(
            name='UserConferenceInterest',
        ),
        
        # Step 2: Delete the Conference model
        migrations.DeleteModel(
            name='Conference',
        ),
        
        # Step 3: Create new Event model
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Event title', max_length=255)),
                ('slug', models.SlugField(help_text='URL-friendly slug auto-generated from title', max_length=255, unique=True)),
                ('description', models.TextField(blank=True, help_text='Detailed description of the event', null=True)),
                ('type', models.CharField(choices=[('conference', 'Conference'), ('workshop', 'Workshop'), ('webinar', 'Webinar'), ('meetup', 'Meetup')], default='conference', help_text='Type of event', max_length=50)),
                ('category', models.CharField(blank=True, help_text='Category of event', max_length=100, null=True)),
                ('tags', models.JSONField(blank=True, help_text='Tags for event organization', null=True)),
                ('start_date', models.DateField(help_text='Conference start date')),
                ('end_date', models.DateField(help_text='Conference end date')),
                ('city', models.CharField(db_index=True, help_text='City where event is held', max_length=100)),
                ('country', models.CharField(help_text='Country where event is held', max_length=100)),
                ('venue', models.CharField(blank=True, help_text='Venue/location details', max_length=255, null=True)),
                ('address', models.TextField(blank=True, help_text='Full address of the event', null=True)),
                ('latitude', models.FloatField(blank=True, help_text='Latitude coordinate', null=True)),
                ('longitude', models.FloatField(blank=True, help_text='Longitude coordinate', null=True)),
                ('timezone', models.CharField(default='UTC', help_text='Timezone of the event', max_length=50)),
                ('organizer_name', models.CharField(blank=True, help_text='Name of event organizer', max_length=255, null=True)),
                ('price_min', models.FloatField(blank=True, help_text='Minimum ticket price', null=True)),
                ('price_max', models.FloatField(blank=True, help_text='Maximum ticket price', null=True)),
                ('currency', models.CharField(default='INR', help_text='Currency for pricing', max_length=10)),
                ('is_free', models.BooleanField(default=False, help_text='Whether the event is free')),
                ('banner_image', models.URLField(blank=True, help_text='URL of banner image', null=True)),
                ('website_url', models.URLField(blank=True, help_text='Official website URL', null=True)),
                ('registration_url', models.URLField(blank=True, help_text='Registration/ticket URL', null=True)),
                ('is_featured', models.BooleanField(default=False, help_text='Whether the event is featured')),
                ('rating', models.FloatField(default=0.0, help_text='Event rating (0-5)')),
                ('interested_count', models.IntegerField(default=0, help_text='Number of users interested in this event')),
                ('source', models.CharField(blank=True, help_text="Source of event information (e.g., 'EventBrite', 'LinkedIn')", max_length=100, null=True)),
                ('source_url', models.URLField(blank=True, help_text='URL of the event source', max_length=500, null=True, unique=True)),
                ('hash', models.CharField(blank=True, help_text='Hash for deduplication', max_length=64, null=True, unique=True)),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Whether this event is active/visible')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Created timestamp')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Last updated timestamp')),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
                'db_table': 'bleisure_event',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['created_at'], name='bleisure_ev_created_xxxxx_idx'),
                    models.Index(fields=['city'], name='bleisure_ev_city_xxxxx_idx'),
                    models.Index(fields=['type'], name='bleisure_ev_type_xxxxx_idx'),
                    models.Index(fields=['start_date'], name='bleisure_ev_start_d_xxxxx_idx'),
                    models.Index(fields=['is_active', '-created_at'], name='bleisure_ev_is_acti_xxxxx_idx'),
                    models.Index(fields=['city', 'start_date'], name='bleisure_ev_city_st_xxxxx_idx'),
                ],
            },
        ),
        
        # Step 4: Create SubEvent model
        migrations.CreateModel(
            name='SubEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='SubEvent title', max_length=255)),
                ('type', models.CharField(choices=[('agenda', 'Agenda'), ('side_event', 'Side Event')], help_text='Type of sub-event', max_length=20)),
                ('start_time', models.DateTimeField(help_text='Start time of sub-event')),
                ('end_time', models.DateTimeField(help_text='End time of sub-event')),
                ('location', models.CharField(blank=True, help_text='Location within venue', max_length=255, null=True)),
                ('description', models.TextField(blank=True, help_text='Description of sub-event', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(help_text='Parent event', on_delete=django.db.models.deletion.CASCADE, related_name='sub_events', to='bleisure.event')),
            ],
            options={
                'verbose_name': 'Sub Event',
                'verbose_name_plural': 'Sub Events',
                'db_table': 'bleisure_sub_event',
                'ordering': ['start_time'],
                'indexes': [
                    models.Index(fields=['event'], name='bleisure_su_event_i_xxxxx_idx'),
                    models.Index(fields=['start_time'], name='bleisure_su_start_t_xxxxx_idx'),
                ],
            },
        ),
        
        # Step 5: Create new UserEventInterest model
        migrations.CreateModel(
            name='UserEventInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When user marked interest')),
                ('event', models.ForeignKey(help_text='Event the user is interested in', on_delete=django.db.models.deletion.CASCADE, related_name='interested_users', to='bleisure.event')),
                ('user', models.ForeignKey(help_text='User who marked interest', on_delete=django.db.models.deletion.CASCADE, related_name='event_interests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Event Interest',
                'verbose_name_plural': 'User Event Interests',
                'db_table': 'bleisure_user_event_interest',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user'], name='bleisure_us_user_id_xxxxx_idx'),
                    models.Index(fields=['event'], name='bleisure_us_event_i_xxxxx_idx'),
                    models.Index(fields=['user', 'event'], name='bleisure_us_user_id_xxxxx_2_idx'),
                ],
                'unique_together': {('user', 'event')},
            },
        ),
        
        # Step 6: Create new UserEventReview model
        migrations.CreateModel(
            name='UserEventReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField(help_text='Rating value (0-5 stars)')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When review was submitted')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When review was last updated')),
                ('event', models.ForeignKey(help_text='Event being reviewed', on_delete=django.db.models.deletion.CASCADE, related_name='user_reviews', to='bleisure.event')),
                ('user', models.ForeignKey(help_text='User who submitted the review', on_delete=django.db.models.deletion.CASCADE, related_name='event_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Event Review',
                'verbose_name_plural': 'User Event Reviews',
                'db_table': 'bleisure_user_event_review',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user'], name='bleisure_us_user_id_xxxxx_3_idx'),
                    models.Index(fields=['event'], name='bleisure_us_event_i_xxxxx_2_idx'),
                    models.Index(fields=['user', 'event'], name='bleisure_us_user_id_xxxxx_3_2_idx'),
                ],
                'unique_together': {('user', 'event')},
            },
        ),
    ]
