# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/dashboards/admin.py
from django.contrib import admin
from .models import Dashboard, Chart

class ChartInline(admin.TabularInline):
    model = Chart
    extra = 0
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'charts_count', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChartInline]
    date_hierarchy = 'created_at'

@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard', 'chart_type', 'created_at']
    list_filter = ['chart_type', 'created_at']
    search_fields = ['name', 'dashboard__name']
    readonly_fields = ['created_at', 'updated_at']