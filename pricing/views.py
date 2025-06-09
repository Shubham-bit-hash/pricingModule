from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import PricingConfig
from .serializers import PricingCalculationSerializer, PricingResultSerializer



class CalculatePriceView(APIView):
    def post(self, request):
        serializer = PricingCalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        day_of_week = data['day_of_week'].strip().upper()  # Normalize input
        
        # Get active config for the given day
        configs = PricingConfig.objects.filter(is_active=True)
        config = None

        for c in configs:
            # Handle both list and CSV string in applicable_days
            if isinstance(c.applicable_days, list):
                if day_of_week in c.applicable_days:
                    config = c
                    break
            elif isinstance(c.applicable_days, str):
                if day_of_week in c.applicable_days.split(","):
                    config = c
                    break
        
        if not config:
            return Response(
                {"error": f"No active pricing configuration found for {day_of_week}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # --- Price Component Calculation ---
        distance = float(data['distance'])
        ride_time_minutes = float(data['ride_time'])
        waiting_time = float(data['waiting_time'])

        # Distance calculation
        if distance <= float(config.base_distance):
            distance_charge = float(config.base_price)
        else:
            additional_distance = distance - float(config.base_distance)
            distance_charge = float(config.base_price) + (additional_distance * float(config.additional_distance_price))

        # Time calculation
        ride_time_hours = ride_time_minutes / 60
        time_charge = 0
        time_multipliers = config.time_multipliers.order_by('order')
        remaining_time = ride_time_hours

        for multiplier in time_multipliers:
            if remaining_time <= 0:
                break
            max_hours = float(multiplier.max_hours)
            applicable_time = min(remaining_time, max_hours)
            time_charge += applicable_time * float(multiplier.multiplier)
            remaining_time -= applicable_time

        # Waiting charge calculation
        waiting_charge = 0
        waiting_config = config.waiting_charges.first()
        if waiting_config:
            if waiting_time > float(waiting_config.initial_wait_time):
                chargeable_time = waiting_time - float(waiting_config.initial_wait_time)
                intervals = chargeable_time / float(waiting_config.interval_duration)
                waiting_charge = intervals * float(waiting_config.charge_per_interval)

        # Total
        total_price = distance_charge + time_charge + waiting_charge

        # --- Response ---
        result = {
            'total_price': round(total_price, 2),
            'base_price': float(config.base_price),
            'distance_charge': round(distance_charge, 2),
            'time_charge': round(time_charge, 2),
            'waiting_charge': round(waiting_charge, 2),
            'config_used': config.name
        }

        # Optional: Save logs
        # PriceCalculationLog.objects.create(
        #     config=config,
        #     distance=distance,
        #     ride_time=ride_time_minutes,
        #     waiting_time=waiting_time,
        #     total_price=total_price
        # )

        return Response(result, status=status.HTTP_200_OK)