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
# 确保正确导入活动记录函数
from activities.utils import create_dashboard_activity, create_visualization_activity
from users.permissions import IsAdminOrAnalyst, IsCreatorOrAdmin


class DashboardListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DashboardSerializer
        return DashboardListSerializer

    def get_queryset(self):
        return Dashboard.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminOrAnalyst()]

    def create(self, request, *args, **kwargs):
        print("🎯 [DashboardListCreateView] CREATE方法被调用 - 强制修复版")
        print(f"🎯 请求用户: {request.user.username}")
        print(f"🎯 请求数据: {request.data}")

        # 使用父类方法创建看板
        response = super().create(request, *args, **kwargs)

        # 🔥 强制创建活动记录
        if response.status_code == 201:
            dashboard_data = response.data
            dashboard_id = dashboard_data.get('id')
            dashboard_name = dashboard_data.get('name')

            print(f"✅ 看板创建成功: {dashboard_name} (ID: {dashboard_id})")
            print("🎯 强制创建活动记录...")

            try:
                # 使用工具函数创建活动记录
                from activities.utils import create_dashboard_activity
                result = create_dashboard_activity(
                    user=request.user,
                    dashboard_name=dashboard_name,
                    dashboard_id=dashboard_id,
                    action='created'
                )

                if result:
                    print(f"✅ 强制活动记录创建成功!")
                    print(f"✅ 活动ID: {result.id}")
                    print(f"✅ 活动描述: {result.description}")
                    print(f"✅ 资源ID: {result.resource_id}")

                    # 🔥 新增：立即验证活动记录是否在数据库中
                    from activities.models import Activity
                    recent_activities = Activity.objects.filter(
                        resource_type='dashboard',
                        resource_id=dashboard_id
                    ).order_by('-created_at')

                    if recent_activities.exists():
                        print(f"✅ 验证成功：在数据库中找到 {recent_activities.count()} 条相关活动记录")
                        for activity in recent_activities[:3]:
                            print(f"   - 活动: {activity.description} (时间: {activity.created_at})")
                    else:
                        print(f"❌ 验证失败：在数据库中未找到相关活动记录")

                else:
                    print(f"❌ 强制活动记录创建失败")

            except Exception as e:
                print(f"❌ 强制活动记录创建失败: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ 看板创建失败，状态码: {response.status_code}")
            print(f"❌ 响应数据: {response.data}")

        return response


class DashboardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DashboardUpdateSerializer
        return DashboardSerializer

    def get_queryset(self):
        return Dashboard.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsCreatorOrAdmin()]
        elif self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsCreatorOrAdmin()]

    def perform_update(self, serializer):
        dashboard = serializer.save()
        # 创建更新活动记录
        create_dashboard_activity(
            user=self.request.user,
            dashboard_name=dashboard.name,
            dashboard_id=dashboard.id,
            action='updated'
        )

    def perform_destroy(self, instance):
        print(f"🔧 [Dashboard] 正在删除看板: {instance.name}, ID: {instance.id}")

        # 在删除之前记录活动
        from activities.utils import create_dashboard_activity
        result = create_dashboard_activity(
            user=self.request.user,
            dashboard_name=instance.name,
            dashboard_id=instance.id,
            action='deleted'
        )

        if result:
            print(f"✅ [Dashboard] 看板删除活动记录已创建: {result.description}")
        else:
            print(f"❌ [Dashboard] 看板删除活动记录创建失败")

        # 检查权限
        if instance.user != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("您只能删除自己创建的看板")

        print(f"✅ [Dashboard] 看板删除权限验证通过")
        super().perform_destroy(instance)


class ChartListCreateView(generics.ListCreateAPIView):
    serializer_class = ChartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        dashboard_id = self.kwargs.get('dashboard_id')
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)
        return Chart.objects.filter(dashboard=dashboard)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdminOrAnalyst()]

    def perform_create(self, serializer):
        dashboard_id = self.kwargs.get('dashboard_id')
        dashboard = get_object_or_404(Dashboard, id=dashboard_id)

        # 检查权限
        if dashboard.user != self.request.user and self.request.user.role != 'admin':
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

    if dashboard.user != request.user and request.user.role != 'admin':
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

    # 创建克隆活动记录
    create_dashboard_activity(
        user=request.user,
        dashboard_name=cloned_dashboard.name,
        dashboard_id=cloned_dashboard.id,
        action='created'
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def debug_create_dashboard(request):
    """调试用：手动创建看板并记录活动"""
    from activities.utils import create_dashboard_activity

    try:
        dashboard = Dashboard.objects.create(
            name="调试看板",
            description="调试用",
            user=request.user,
            layout_config={},
            chart_configs=[],
            is_public=False
        )

        print(f"🔧 [Debug] 手动创建看板: {dashboard.name}, ID: {dashboard.id}")

        # 手动创建活动记录
        activity = create_dashboard_activity(
            user=request.user,
            dashboard_name=dashboard.name,
            dashboard_id=dashboard.id,
            action='created'
        )

        if activity:
            print(f"✅ [Debug] 成功创建活动记录: {activity.description}")
            return Response({
                'success': True,
                'dashboard_id': dashboard.id,
                'activity_id': activity.id,
                'message': '调试看板和活动记录创建成功'
            })
        else:
            print(f"❌ [Debug] 创建活动记录失败")
            return Response({
                'success': False,
                'message': '创建活动记录失败'
            }, status=400)

    except Exception as e:
        print(f"❌ [Debug] 调试失败: {str(e)}")
        return Response({
            'success': False,
            'message': f'调试失败: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debug_activities(request):
    """调试用：检查活动记录"""
    from activities.models import Activity
    from activities.serializers import ActivitySerializer

    # 获取所有活动记录
    all_activities = Activity.objects.all().order_by('-created_at')[:20]

    # 检查是否有看板创建活动
    dashboard_activities = Activity.objects.filter(
        activity_type='dashboard_created'
    ).order_by('-created_at')[:10]

    print(f"🔍 [Debug] 总活动记录数: {all_activities.count()}")
    print(f"🔍 [Debug] 看板创建活动数: {dashboard_activities.count()}")

    for activity in dashboard_activities:
        print(f"📋 看板活动: {activity.description} (ID: {activity.id}, 时间: {activity.created_at})")

    return Response({
        'all_activities_count': all_activities.count(),
        'dashboard_activities_count': dashboard_activities.count(),
        'recent_dashboard_activities': ActivitySerializer(dashboard_activities, many=True).data,
        'all_activities': ActivitySerializer(all_activities, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def force_create_activity(request, dashboard_id):
    """强制为看板创建活动记录"""
    from activities.utils import create_dashboard_activity
    from activities.models import Activity

    try:
        dashboard = Dashboard.objects.get(id=dashboard_id)

        print(f"🎯 强制为看板创建活动记录: {dashboard.name} (ID: {dashboard.id})")

        # 方法1：使用工具函数
        activity = create_dashboard_activity(
            user=request.user,
            dashboard_name=dashboard.name,
            dashboard_id=dashboard.id,
            action='created'
        )

        if activity:
            return Response({
                'success': True,
                'message': f'成功为看板 "{dashboard.name}" 创建活动记录',
                'activity_id': activity.id
            })
        else:
            # 方法2：直接创建
            from activities.models import ActivityType
            direct_activity = Activity.objects.create(
                user=request.user,
                activity_type=ActivityType.DASHBOARD_CREATED,
                description=f'创建了数据看板 "{dashboard.name}"',
                resource_type='dashboard',
                resource_id=dashboard.id,
                resource_name=dashboard.name
            )
            return Response({
                'success': True,
                'message': f'直接创建活动记录成功',
                'activity_id': direct_activity.id
            })

    except Dashboard.DoesNotExist:
        return Response({'success': False, 'message': '看板不存在'}, status=404)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)
