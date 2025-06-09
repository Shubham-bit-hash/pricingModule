from django.db import models
from django.core.validators import MinValueValidator

class PricingConfig(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    applicable_days = models.JSONField(default=list)  # Stores list of days like ['MON', 'TUE']
    base_distance = models.DecimalField(max_digits=5, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_distance_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TimeMultiplier(models.Model):
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='time_multipliers')
    max_hours = models.DecimalField(max_digits=5, decimal_places=2)
    multiplier = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

class WaitingCharge(models.Model):
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='waiting_charges')
    initial_wait_time = models.PositiveIntegerField(help_text="Initial free wait time in minutes")
    charge_per_interval = models.DecimalField(max_digits=10, decimal_places=2)
    interval_duration = models.PositiveIntegerField(help_text="Interval duration in minutes")

class PricingConfigLog(models.Model):
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE)
    changed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    change_details = models.JSONField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.pricing_config.name} at {self.changed_at}"