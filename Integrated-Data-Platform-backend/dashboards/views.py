# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/dashboards/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Dashboard, Chart
from .serializers import (
    DashboardSerializer, DashboardListSerializer,
    DashboardUpdateSerializer, ChartSerializer
)
from activities.utils import create_dashboard_activity  # 导入活动创建函数


class DashboardListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DashboardSerializer
        return DashboardListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Dashboard.objects.all()
        else:
            return Dashboard.objects.filter(user=user) | Dashboard.objects.filter(is_public=True)

    def perform_create(self, serializer):
        dashboard = serializer.save(user=self.request.user)
        # 创建活动记录
        create_dashboard_activity(
            user=self.request.user,
            dashboard_name=dashboard.name,
            dashboard_id=dashboard.id,
            action='created'
        )


class DashboardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DashboardUpdateSerializer
        return DashboardSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Dashboard.objects.all()
        else:
            return Dashboard.objects.filter(user=user) | Dashboard.objects.filter(is_public=True)

    def perform_update(self, serializer):
        dashboard = serializer.save()
        # 创建更新活动记录
        create_dashboard_activity(
            user=self.request.user,
            dashboard_name=dashboard.name,
            dashboard_id=dashboard.id,
            action='updated'
        )


class ChartListCreateView(generics.ListCreateAPIView):
    serializer_class = ChartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        dashboard_id = self.kwargs.get('dashboard_id')
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)
        if not (dashboard.user == self.request.user or dashboard.is_public or self.request.user.is_staff):
            raise permissions.PermissionDenied("您没有权限查看此看板的图表")
        return Chart.objects.filter(dashboard=dashboard)

    def perform_create(self, serializer):
        dashboard_id = self.kwargs.get('dashboard_id')
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)
        if dashboard.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("您没有权限在此看板添加图表")
        chart = serializer.save(dashboard=dashboard)
        # 创建图表添加活动记录
        create_visualization_activity(
            user=self.request.user,
            visualization_name=chart.name,
            visualization_id=chart.id,
            action='created'
        )

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_dashboard_layout(request, pk):
    dashboard = get_object_or_404(Dashboard, id=pk)
    if dashboard.user != request.user and not request.user.is_staff:
        return Response(
            {"error": "您没有权限修改此看板"},
            status=status.HTTP_403_FORBIDDEN
        )

    layout_config = request.data.get('layout_config')
    if layout_config is not None:
        dashboard.layout_config = layout_config
        dashboard.save()
        return Response({"message": "布局更新成功"})

    return Response(
        {"error": "缺少布局配置"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def clone_dashboard(request, pk):
    """克隆看板"""
    original_dashboard = get_object_or_404(Dashboard, id=pk)

    # 检查权限：只能克隆自己的看板或公开看板
    if not original_dashboard.is_public and original_dashboard.user != request.user:
        return Response(
            {"error": "您没有权限克隆此看板"},
            status=status.HTTP_403_FORBIDDEN
        )

    # 创建克隆
    cloned_dashboard = Dashboard.objects.create(
        name=f"{original_dashboard.name} (副本)",
        description=original_dashboard.description,
        user=request.user,
        layout_config=original_dashboard.layout_config,
        chart_configs=original_dashboard.chart_configs,
        is_public=False
    )

    # 克隆图表
    for chart in original_dashboard.charts.all():
        Chart.objects.create(
            dashboard=cloned_dashboard,
            name=chart.name,
            chart_type=chart.chart_type,
            dataset_id=chart.dataset_id,
            config=chart.config,
            position=chart.position
        )

    serializer = DashboardSerializer(cloned_dashboard)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
