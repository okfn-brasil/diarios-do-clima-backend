from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'pagseguro_plan_id',
    )