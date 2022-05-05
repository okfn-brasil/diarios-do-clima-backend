from django.contrib import admin
from .models import PlanSubscription, PlanSubscriptionStatus


class PlanSubscriptionStatusInline(admin.StackedInline):
    model = PlanSubscriptionStatus
    extra = 0


@admin.register(PlanSubscription)
class PlanSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'plan',
        'created_at',
    )

    inlines = (
        PlanSubscriptionStatusInline,
    )

@admin.register(PlanSubscriptionStatus)
class PlanSubscriptionStatus(admin.ModelAdmin):
    list_display = (
        'id',
        'pagseguro_data',
        'pagseguro_notification_code'
    )

    list_filter = (
        'pagseguro_data',
    )

    search_fields = (
        'pagseguro_notification_code',
    )
