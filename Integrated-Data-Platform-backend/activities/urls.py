# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityListCreateView.as_view(), name='activity-list-create'),
    path('recent/', views.RecentActivitiesView.as_view(), name='recent-activities'),
    # 移除了不存在的 UserActivitiesView
]