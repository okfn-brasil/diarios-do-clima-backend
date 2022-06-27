from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'territory_id',
        'query_string',
        'created_at',
    )

    list_filter = (
        'user',
        'created_at',
    )
