# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Activity
from .serializers import ActivitySerializer, RecentActivitySerializer


class ActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecentActivitiesView(generics.ListAPIView):
    serializer_class = RecentActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        获取最近活动记录 - 简化版本，只从数据库读取
        """
        # 获取最近30天的活动记录
        thirty_days_ago = timezone.now() - timedelta(days=30)
        queryset = Activity.objects.filter(
            created_at__gte=thirty_days_ago
        ).select_related('user').order_by('-created_at')

        print(f"📊 [RecentActivitiesView] 从数据库查询到 {queryset.count()} 条活动记录")

        # 记录最新的几条活动用于调试
        recent_activities = queryset[:5]
        for activity in recent_activities:
            print(f"   - {activity.description} (时间: {activity.created_at})")

        return queryset[:100]  # 限制返回数量