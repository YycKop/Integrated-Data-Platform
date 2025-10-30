# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/ai/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'models', views.AIModelViewSet, basename='ai-model')
router.register(r'tasks', views.PredictionTaskViewSet, basename='prediction-task')

urlpatterns = [
    path('', include(router.urls)),

    # 数据集相关接口
    path('datasets/', views.AIModelViewSet.as_view({'get': 'datasets'}), name='ai-datasets'),
    path('datasets/columns/', views.AIModelViewSet.as_view({'get': 'dataset_columns'}), name='ai-dataset-columns'),
    path('datasets/preview/', views.AIModelViewSet.as_view({'get': 'dataset_preview'}), name='ai-dataset-preview'),

    # 状态更新接口
    path('models/<int:pk>/update_status/', views.AIModelViewSet.as_view({'post': 'update_status'}),
         name='ai-model-update-status'),
    path('models/<int:pk>/start_training/', views.AIModelViewSet.as_view({'post': 'start_training'}),
         name='ai-model-start-training'),
    path('models/<int:pk>/complete_training/', views.AIModelViewSet.as_view({'post': 'complete_training'}),
         name='ai-model-complete-training'),

    # 分析接口
    path('analyze-market-trends/', views.analyze_market_trends, name='analyze-market-trends'),
    path('generate-insights/', views.generate_insights, name='generate-insights'),
]