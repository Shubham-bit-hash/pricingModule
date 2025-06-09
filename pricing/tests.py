# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from rest_framework.test import APIClient
# from rest_framework import status
# from .models import PricingConfig, TimeMultiplier, WaitingCharge

# User = get_user_model()

# class PricingCalculationTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
        
#         # Create a test pricing config
#         self.config = PricingConfig.objects.create(
#             name="Weekday Pricing",
#             is_active=True,
#             applicable_days=['MON', 'TUE', 'WED', 'THU', 'FRI'],
#             base_distance=3.0,
#             base_price=80.00,
#             additional_distance_price=30.00
#         )
        
#         # Add time multipliers
#         TimeMultiplier.objects.create(
#             pricing_config=self.config,
#             max_hours=1.0,
#             multiplier=1.0,
#             order=1
#         )
#         TimeMultiplier.objects.create(
#             pricing_config=self.config,
#             max_hours=1.0,
#             multiplier=1.25,
#             order=2
#         )
        
#         # Add waiting charges
#         WaitingCharge.objects.create(
#             pricing_config=self.config,
#             initial_wait_time=3,
#             charge_per_interval=5.00,
#             interval_duration=3
#         )
    
#     def test_base_price_calculation(self):
#         """Test calculation for distance within base distance"""
#         data = {
#             'distance': 2.5,
#             'ride_time': 45,
#             'waiting_time': 2,
#             'day_of_week': 'MON'
#         }
#         response = self.client.post('/api/calculate-price/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['distance_charge'], 80.00)
#         self.assertEqual(response.data['time_charge'], 0.75)  # 45min = 0.75h * 1.0
#         self.assertEqual(response.data['waiting_charge'], 0.00)
    
#     def test_additional_distance_calculation(self):
#         """Test calculation with additional distance"""
#         data = {
#             'distance': 4.0,
#             'ride_time': 90,
#             'waiting_time': 5,
#             'day_of_week': 'TUE'
#         }
#         response = self.client.post('/api/calculate-price/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['distance_charge'], 80.00 + 30.00)  # 1km additional
#         self.assertEqual(response.data['time_charge'], 1.0 + (0.5 * 1.25))  # 1h@1x + 0.5h@1.25x
#         self.assertEqual(response.data['waiting_charge'], 5.00)  # 2min over initial 3
    
#     def test_no_active_config(self):
#         """Test when no active config exists for the day"""
#         data = {
#             'distance': 2.5,
#             'ride_time': 45,
#             'waiting_time': 2,
#             'day_of_week': 'SUN'
#         }
#         response = self.client.post('/api/calculate-price/', data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# class PricingConfigLogTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_superuser(
#             username='admin',
#             password='testpass123',
#             email='admin@example.com'
#         )
#         self.config = PricingConfig.objects.create(
#             name="Test Config",
#             is_active=True,
#             applicable_days=['MON'],
#             base_distance=3.0,
#             base_price=80.00,
#             additional_distance_price=30.00
#         )
    
#     def test_config_change_logging(self):
#         """Test that config changes are logged"""
#         self.client.force_login(self.user)
#         url = f'/admin/pricing/pricingconfig/{self.config.id}/change/'
#         data = {
#             'name': 'Updated Config',
#             'is_active': True,
#             'applicable_days': ['MON', 'TUE'],
#             'base_distance': 3.5,
#             'base_price': 85.00,
#             'additional_distance_price': 28.00,
#             'time_multipliers-TOTAL_FORMS': 0,
#             'time_multipliers-INITIAL_FORMS': 0,
#             'waiting_charges-TOTAL_FORMS': 0,
#             'waiting_charges-INITIAL_FORMS': 0,
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 302)  # Successful redirect
        
#         logs = self.config.pricingconfiglog_set.all()
#         self.assertEqual(logs.count(), 1)
#         self.assertIn('name', logs[0].change_details['changes'][0]['field'])
#         self.assertIn('base_price', logs[0].change_details['changes'][0]['field'])

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import PricingConfig, TimeMultiplier, WaitingCharge

class CalculatePriceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('calculate-price')  # Make sure your URL is named

        # Create pricing config for MON and TUE
        self.config = PricingConfig.objects.create(
            name="weekday pricing",
            base_price=80,
            base_distance=5,
            additional_distance_price=30,
            applicable_days=["MON", "TUE"],
            is_active=True
        )

        # Add time multiplier
        TimeMultiplier.objects.create(
            pricing_config=self.config,
            multiplier=1.1,
            max_hours=2,
            order=1
        )

        # Add waiting charge rule
        WaitingCharge.objects.create(
            pricing_config=self.config,
            initial_wait_time=5,
            interval_duration=2,
            charge_per_interval=2.5
        )

    def test_monday_price_calculation(self):
        data = {
            "distance": 8.5,
            "ride_time": 95,
            "waiting_time": 10,
            "day_of_week": "MON"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_price', response.data)
        self.assertEqual(response.data['config_used'], "weekday pricing")

    def test_price_calculation_for_tuesday(self):
        data = {
            "distance": 6,
            "ride_time": 60,
            "waiting_time": 6,
            "day_of_week": "TUE"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_day_with_no_config(self):
        data = {
            "distance": 10,
            "ride_time": 50,
            "waiting_time": 5,
            "day_of_week": "SUN"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_invalid_input_data(self):
        data = {
            "distance": -5,
            "ride_time": "invalid",
            "waiting_time": 10,
            "day_of_week": "MON"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
