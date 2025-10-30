# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/dashboards/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardListCreateView.as_view(), name='dashboard-list-create'),
    path('<int:pk>/', views.DashboardDetailView.as_view(), name='dashboard-detail'),
    path('<int:pk>/layout/', views.update_dashboard_layout, name='dashboard-layout'),
    path('<int:pk>/clone/', views.clone_dashboard, name='dashboard-clone'),
    path('<int:dashboard_id>/charts/', views.ChartListCreateView.as_view(), name='chart-list-create'),
]