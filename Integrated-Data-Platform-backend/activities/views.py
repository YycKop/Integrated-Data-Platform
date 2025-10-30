# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/views.py
from rest_framework import generics, permissions
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
        seven_days_ago = timezone.now() - timedelta(days=7)
        return Activity.objects.filter(
            user=self.request.user,
            created_at__gte=seven_days_ago
        ).order_by('-created_at')[:20]