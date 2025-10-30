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
    created_by = serializers.CharField(source='user.username', read_only=True)
    items = serializers.ListField(write_only=True, required=False, allow_empty=True, default=[])

    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'user', 'created_by',
            'layout_config', 'chart_configs', 'is_public',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("🔧 [DashboardSerializer] 序列化器初始化 - 开始")
        print(f"🔧 [DashboardSerializer] 上下文: {self.context}")
        print("🔧 [DashboardSerializer] 序列化器初始化 - 结束")

    def validate(self, attrs):
        print("🔧 [DashboardSerializer] 验证数据 - 开始")
        print(f"🔧 [DashboardSerializer] 验证前的数据: {attrs}")
        validated_data = super().validate(attrs)
        print(f"🔧 [DashboardSerializer] 验证后的数据: {validated_data}")
        print("🔧 [DashboardSerializer] 验证数据 - 结束")
        return validated_data

    def create(self, validated_data):
        print("🔧 [DashboardSerializer] CREATE方法被调用 - 简化版")

        # 提取items字段但不处理，由视图处理
        items = validated_data.pop('items', [])
        print(f"🔧 items数据: {items}")

        # 确保user字段正确设置
        if 'user' not in validated_data and 'request' in self.context:
            validated_data['user'] = self.context['request'].user

        # 创建看板（不处理chart_configs，由视图处理）
        dashboard = super().create(validated_data)
        print(f"✅ 看板创建成功: {dashboard.name} (ID: {dashboard.id})")

        return dashboard


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
