from django.contrib import admin
from .models import User
from subscriptions.models import PlanSubscription

class PlanSubscriptionsInlineAdmin(admin.StackedInline):
    model = PlanSubscription
    extra = 0

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'full_name',
        'city',
        'state',
    )

    search_fields = (
        'email',
        'full_name',
    )

    inlines = (
        PlanSubscriptionsInlineAdmin,
    )
