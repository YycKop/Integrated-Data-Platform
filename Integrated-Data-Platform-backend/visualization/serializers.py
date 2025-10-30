# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/visualization/serializers.py
from rest_framework import serializers
from .models import ChartType, Visualization, Dashboard, DashboardItem


class ChartTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartType
        fields = '__all__'


class VisualizationSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    dataset_name = serializers.CharField(source='dataset.name', read_only=True)
    chart_type_name = serializers.CharField(source='chart_type.name', read_only=True)

    class Meta:
        model = Visualization
        fields = '__all__'


class DashboardItemSerializer(serializers.ModelSerializer):
    visualization_name = serializers.CharField(source='visualization.name', read_only=True)

    class Meta:
        model = DashboardItem
        fields = '__all__'


class DashboardSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    items_detail = DashboardItemSerializer(source='dashboarditem_set', many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = '__all__'