# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/admin.py
from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'resource_type', 'resource_name', 'created_at']
    list_filter = ['activity_type', 'resource_type', 'created_at']
    search_fields = ['user__username', 'description', 'resource_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'