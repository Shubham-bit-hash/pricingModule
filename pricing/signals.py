

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PricingConfig, PricingConfigLog
import decimal

User = get_user_model()

# 👇 Decimal converter
def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(elem) for elem in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj

@receiver(post_save, sender=PricingConfig)
def log_pricing_config_change(sender, instance, created, **kwargs):
    if not created:  # We only log updates, not initial creation
        request = getattr(instance, '_request', None)
        user = request.user if request and hasattr(request, 'user') else None
        
        # Get the changed fields
        changed_fields = []
        for field in instance._meta.fields:
            field_name = field.name
            if field_name in ['updated_at', 'created_at']:
                continue
            old_value = getattr(instance, f'_original_{field_name}', None)
            new_value = getattr(instance, field_name)
            if old_value != new_value:
                changed_fields.append({
                    'field': field_name,
                    'old': old_value,
                    'new': new_value
                })
        
        if changed_fields:
            # 👇 Ensure no Decimal goes into JSONField
            safe_changes = convert_decimals({'changes': changed_fields})
            PricingConfigLog.objects.create(
                pricing_config=instance,
                changed_by=user,
                change_details=safe_changes
            )

# 👇 Decorator for Django admin to track changes
def track_changes(model):
    def wrapper(func):
        def inner(request, obj, form, change):
            if change:  # Only for existing objects
                for field in obj._meta.fields:
                    field_name = field.name
                    setattr(obj, f'_original_{field_name}', getattr(obj, field_name))
            obj._request = request
            return func(request, obj, form, change)
        return inner
    return wrapper
