from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import UserProfile

User = get_user_model()


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
    
    def test_create_user_profile(self):
        """Test creating a user profile."""
        profile = UserProfile.objects.create(
            user=self.user,
            role='Developer',
            industry='Technology',
            interest='Backend Development',
            budget=100000,
            location_city='New York',
            location_country='USA'
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, 'Developer')
        self.assertEqual(profile.industry, 'Technology')
    
    def test_one_to_one_relationship(self):
        """Test one-to-one relationship between User and UserProfile."""
        profile1 = UserProfile.objects.create(
            user=self.user,
            role='Developer',
            industry='Technology',
            location_city='NYC',
            location_country='USA'
        )
        
        # Should be able to access profile from user
        self.assertEqual(self.user.profile, profile1)
    
    def test_user_profile_str_method(self):
        """Test string representation of UserProfile."""
        profile = UserProfile.objects.create(
            user=self.user,
            role='Designer',
            industry='Design',
            location_city='Mumbai',
            location_country='India'
        )
        
        expected_str = f"Profile of {self.user.email} - {self.user.full_name}"
        self.assertEqual(str(profile), expected_str)


class OnboardingAPIViewTest(TestCase):
    """Test cases for Onboarding API."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='onboard@example.com',
            password='testpass123',
            full_name='Onboard User'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_onboarding_create_profile(self):
        """Test creating a new profile via onboarding API."""
        data = {
            'role': 'UI Designer',
            'industry': 'Design',
            'interest': 'Product Design',
            'budget': 200000,
            'location_city': 'Mumbai',
            'location_country': 'India',
            'linkedin_text': 'I am a designer'
        }
        
        response = self.client.post('/api/bleisure/onboarding/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Profile created successfully')
    
    def test_onboarding_update_existing_profile(self):
        """Test updating an existing profile via onboarding API."""
        # Create initial profile
        UserProfile.objects.create(
            user=self.user,
            role='Developer',
            industry='Technology',
            location_city='NYC',
            location_country='USA'
        )
        
        # Update profile
        data = {
            'role': 'Product Manager',
            'industry': 'Technology',
            'interest': 'Product Management',
            'budget': 300000,
            'location_city': 'San Francisco',
            'location_country': 'USA'
        }
        
        response = self.client.post('/api/bleisure/onboarding/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Profile updated successfully')
    
    def test_onboarding_validation_failure(self):
        """Test onboarding with invalid data."""
        data = {
            'role': 'Designer',
            'industry': 'Design',
            # Missing required fields
        }
        
        response = self.client.post('/api/bleisure/onboarding/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_onboarding_unauthenticated_access(self):
        """Test onboarding requires authentication."""
        self.client.force_authenticate(user=None)
        
        data = {
            'role': 'Designer',
            'industry': 'Design',
            'interest': 'UI Design',
            'budget': 100000,
            'location_city': 'Mumbai',
            'location_country': 'India'
        }
        
        response = self.client.post('/api/bleisure/onboarding/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileRetrieveAPIViewTest(TestCase):
    """Test cases for Profile Retrieve API."""
    
    def setUp(self):
        """Set up test client and user with profile."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='testpass123',
            full_name='Profile User'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='Developer',
            industry='Technology',
            interest='Backend Development',
            budget=100000,
            location_city='NYC',
            location_country='USA'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_user_profile(self):
        """Test retrieving user profile."""
        response = self.client.get('/api/bleisure/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['user_email'], self.user.email)
        self.assertEqual(response.data['data']['role'], 'Developer')
    
    def test_retrieve_profile_not_found(self):
        """Test retrieving profile when it doesn't exist."""
        # Create new user without profile
        user2 = User.objects.create_user(
            email='noprofile@example.com',
            password='testpass123',
            full_name='No Profile User'
        )
        self.client.force_authenticate(user=user2)
        
        response = self.client.get('/api/bleisure/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])


class UserProfileUpdateAPIViewTest(TestCase):
    """Test cases for Profile Update API."""
    
    def setUp(self):
        """Set up test client and user with profile."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='update@example.com',
            password='testpass123',
            full_name='Update User'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='Developer',
            industry='Technology',
            location_city='NYC',
            location_country='USA'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_partial_update_profile(self):
        """Test partial update of user profile."""
        data = {
            'budget': 200000,
            'location_city': 'San Francisco'
        }
        
        response = self.client.patch('/api/bleisure/profile/update/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify updated values
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.budget, 200000)
        self.assertEqual(self.profile.location_city, 'San Francisco')
        # Original value should remain
        self.assertEqual(self.profile.role, 'Developer')


class OnboardingStatusAPIViewTest(TestCase):
    """Test cases for Onboarding Status API."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='status@example.com',
            password='testpass123',
            full_name='Status User'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_onboarding_status_not_completed(self):
        """Test checking onboarding status when not completed."""
        response = self.client.get('/api/bleisure/onboarding-status/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['onboarded'])
    
    def test_onboarding_status_completed(self):
        """Test checking onboarding status when completed."""
        UserProfile.objects.create(
            user=self.user,
            role='Developer',
            industry='Technology',
            location_city='NYC',
            location_country='USA'
        )
        
        response = self.client.get('/api/bleisure/onboarding-status/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['onboarded'])
        self.assertIsNotNone(response.data['data'])
