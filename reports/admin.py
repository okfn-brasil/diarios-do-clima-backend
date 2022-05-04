from atexit import register
from django.contrib import admin
from .models import Report, ReportUserAccess


class ReportUserAccessInline(admin.StackedInline):
    model = ReportUserAccess
    extra = 0
    autocomplete_fields = (
        'user',
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'file',
        'is_public',
    )

    inlines = (
        ReportUserAccessInline,
    )
