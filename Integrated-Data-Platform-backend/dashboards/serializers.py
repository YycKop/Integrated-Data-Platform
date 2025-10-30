# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/dashboards/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Dashboard, Chart

User = get_user_model()


class ChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chart
        fields = [
            'id', 'name', 'chart_type', 'dataset_id', 'config',
            'position', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    charts_count = serializers.IntegerField(read_only=True)
    charts = ChartSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'user', 'user_name',
            'layout_config', 'chart_configs', 'is_public',
            'charts_count', 'charts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DashboardListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    charts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'user_name',
            'charts_count', 'is_public', 'created_at', 'updated_at'
        ]


class DashboardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = [
            'name', 'description', 'layout_config',
            'chart_configs', 'is_public'
        ]