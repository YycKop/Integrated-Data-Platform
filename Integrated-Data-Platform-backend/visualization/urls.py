# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/visualization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChartTypeViewSet, VisualizationViewSet, DashboardViewSet

router = DefaultRouter()
router.register(r'chart-types', ChartTypeViewSet)
router.register(r'visualizations', VisualizationViewSet)
router.register(r'dashboards', DashboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('debug-dashboard-create/', views.debug_dashboard_create, name='debug-dashboard-create'),
]
