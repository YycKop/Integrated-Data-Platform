# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/Integrated-Data-Platform/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 导入其他应用的视图集
from datasets.views import DataSourceViewSet, DatasetViewSet, DataRecordViewSet
from processing.views import ProcessingPipelineViewSet
from visualization.views import ChartTypeViewSet, VisualizationViewSet, DashboardViewSet
from users.views import UserRegistrationView, user_login, user_logout, UserProfileView, get_csrf_token

# ==================== 路由器配置 ====================
# 创建Django REST Framework的默认路由器
# DefaultRouter会自动生成API根视图和标准的RESTful路由
router = DefaultRouter()

# 注册数据集相关的视图集
router.register(r'data-sources', DataSourceViewSet, basename='data-source')  # 数据源管理
router.register(r'datasets', DatasetViewSet, basename='dataset')  # 数据集管理
router.register(r'data-records', DataRecordViewSet, basename='data-record')  # 数据记录管理

# 注册数据处理相关的视图集
router.register(r'processing-pipelines', ProcessingPipelineViewSet, basename='processing-pipeline')  # 处理流水线

# 注册可视化相关的视图集
router.register(r'chart-types', ChartTypeViewSet, basename='chart-type')  # 图表类型管理
router.register(r'visualizations', VisualizationViewSet, basename='visualization')  # 可视化配置
router.register(r'dashboards', DashboardViewSet, basename='dashboard')  # 仪表板管理

# ==================== URL模式配置 ====================
urlpatterns = [
    # Django管理员后台
    path('admin/', admin.site.urls),

    # API路由 - 包含所有通过路由器注册的视图集
    # 访问示例: /api/data-sources/, /api/datasets/, /api/processing-pipelines/ 等
    path('api/', include(router.urls)),

    # AI模块的URLs - 包含AI应用自定义的路由配置
    # AI模块可能有特殊的路由需求，如模型训练、预测等端点
    path('api/ai/', include('ai.urls')),

    # ==================== 自定义API端点 ====================

    # 数据集预览功能 - 自定义动作路由
    # 这种格式用于为视图集的额外动作创建独立URL
    # 访问示例: GET /api/datasets/1/preview/ 预览ID为1的数据集
    path('api/datasets/<int:pk>/preview/',
         DatasetViewSet.as_view({'get': 'preview'}),
         name='dataset-preview'),

    # ==================== 用户认证相关端点 ====================

    # 用户注册 - 基于类的视图
    # 访问: POST /api/auth/register/ 创建新用户
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),

    # 用户登录 - 基于函数的视图
    # 访问: POST /api/auth/login/ 用户登录
    path('api/auth/login/', user_login, name='login'),

    # 用户登出 - 基于函数的视图
    # 访问: POST /api/auth/logout/ 用户登出
    path('api/auth/logout/', user_logout, name='logout'),

    # 用户资料 - 基于类的视图
    # 访问: GET/PUT /api/auth/profile/ 获取或更新用户资料
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),

    # CSRF Token获取 - 基于函数的视图
    # 访问: GET /api/auth/csrf/ 获取CSRF token用于表单提交
    path('api/auth/csrf/', get_csrf_token, name='csrf_token'),
    path('api/activities/', include('activities.urls')),
    path('api/dashboards/', include('dashboards.urls')),
]