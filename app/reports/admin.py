from atexit import register
from django.contrib import admin
from .models import Report, ReportUserAccess, Quotation


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


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'created_at',
    )

    search_fields = (
        'id',
        'email',
        'name',
    )

    list_filter = (
        'created_at',
    )
