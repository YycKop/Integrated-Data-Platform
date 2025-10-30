# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Activity

User = get_user_model()


class ActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'user', 'user_name', 'activity_type', 'activity_type_display',
            'description', 'resource_type', 'resource_id', 'resource_name',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class RecentActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'user_name', 'activity_type', 'activity_type_display',
            'description', 'resource_type', 'resource_id', 'resource_name',
            'timestamp'
        ]