from rest_framework import serializers
from .models import PricingConfig

class PricingCalculationSerializer(serializers.Serializer):
    distance = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    ride_time = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    waiting_time = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    day_of_week = serializers.ChoiceField(choices=PricingConfig.DAY_CHOICES)

class PricingResultSerializer(serializers.Serializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    distance_charge = serializers.DecimalField(max_digits=10, decimal_places=2)
    time_charge = serializers.DecimalField(max_digits=10, decimal_places=2)
    waiting_charge = serializers.DecimalField(max_digits=10, decimal_places=2)
    config_used = serializers.CharField()