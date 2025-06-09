from django.contrib import admin
from django import forms
from .models import PricingConfig, TimeMultiplier, WaitingCharge, PricingConfigLog

class TimeMultiplierInline(admin.TabularInline):
    model = TimeMultiplier
    extra = 1
    min_num = 1

class WaitingChargeInline(admin.StackedInline):
    model = WaitingCharge
    extra = 1
    min_num = 1

class PricingConfigForm(forms.ModelForm):
    class Meta:
        model = PricingConfig
        fields = '__all__'
        widgets = {
            'applicable_days': forms.CheckboxSelectMultiple(
                choices=PricingConfig.DAY_CHOICES
            ),
        }

    def clean_applicable_days(self):
        days = self.cleaned_data.get('applicable_days', [])
        if not days:
            raise forms.ValidationError("At least one day must be selected")
        return days

@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    form = PricingConfigForm
    inlines = [TimeMultiplierInline, WaitingChargeInline]
    list_display = ('name', 'is_active', 'base_distance', 'base_price', 'applicable_days_list')
    list_filter = ('is_active',)
    search_fields = ('name',)
    
    def applicable_days_list(self, obj):
        return ", ".join(dict(PricingConfig.DAY_CHOICES).get(day) for day in obj.applicable_days)
    applicable_days_list.short_description = 'Applicable Days'

@admin.register(PricingConfigLog)
class PricingConfigLogAdmin(admin.ModelAdmin):
    list_display = ('pricing_config', 'changed_by', 'changed_at')
    list_filter = ('changed_at',)
    search_fields = ('pricing_config__name', 'changed_by__username')
    readonly_fields = ('pricing_config', 'changed_by', 'change_details', 'changed_at')
    
    def has_add_permission(self, request):
        return False