# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActivityListCreateView.as_view(), name='activity-list-create'),
    path('recent/', views.RecentActivitiesView.as_view(), name='recent-activities'),
    # 暂时注释掉同步端点，先确保基本功能正常
    # path('sync/', views.ActivitySyncView.as_view(), name='activity-sync'),
]