# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/utils.py
from .models import Activity, ActivityType
from django.contrib.auth import get_user_model

User = get_user_model()


def create_activity(user, activity_type, description, resource_type=None, resource_id=None, resource_name=None,
                    metadata=None):
    """
    创建活动记录的辅助函数
    """
    try:
        print(f"🎯 [create_activity] 开始创建活动记录")
        print(f"🎯 用户: {user.username}")
        print(f"🎯 活动类型: {activity_type}")
        print(f"🎯 描述: {description}")
        print(f"🎯 资源类型: {resource_type}")
        print(f"🎯 资源ID: {resource_id}")
        print(f"🎯 资源名称: {resource_name}")

        # 验证用户
        if not user or not user.is_authenticated:
            print(f"❌ 用户未认证，无法创建活动记录")
            return None

        # 创建活动记录
        activity_data = {
            'user': user,
            'activity_type': activity_type,
            'description': description,
            'resource_type': resource_type or '',
            'resource_id': resource_id,
            'resource_name': resource_name or '',
            'metadata': metadata or {}
        }

        activity = Activity.objects.create(**activity_data)
        print(f"✅ 成功创建活动记录: {activity.id} - {description}")

        return activity

    except Exception as e:
        print(f"❌ 创建活动记录失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return None


def create_dashboard_activity(user, dashboard_name, dashboard_id, action='created'):
    """创建看板相关活动 - 使用正确的活动类型"""
    try:
        print(f"🎯 [create_dashboard_activity] 开始创建看板活动")
        print(f"🎯 用户: {user.username}")
        print(f"🎯 看板名称: {dashboard_name}")
        print(f"🎯 看板ID: {dashboard_id}")
        print(f"🎯 操作: {action}")

        # 根据操作类型选择正确的活动类型
        if action == 'created':
            activity_type = ActivityType.DASHBOARD_CREATED
            description = f'{user.username} 创建了看板 "{dashboard_name}"'
        elif action == 'updated':
            activity_type = ActivityType.DASHBOARD_UPDATED
            description = f'{user.username} 更新了看板 "{dashboard_name}"'
        elif action == 'deleted':
            activity_type = ActivityType.DASHBOARD_DELETED
            description = f'{user.username} 删除了看板 "{dashboard_name}"'
        else:
            activity_type = ActivityType.DASHBOARD_CREATED
            description = f'{user.username} 操作了看板 "{dashboard_name}"'

        result = create_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            resource_type='dashboard',
            resource_id=dashboard_id,
            resource_name=dashboard_name
        )

        if result:
            print(f"✅ 看板活动记录创建成功: {description}")
        else:
            print(f"❌ 看板活动记录创建失败")

        return result

    except Exception as e:
        print(f"❌ 创建看板活动失败: {str(e)}")
        return None


def create_dataset_activity(user, dataset_name, dataset_id, action='created'):
    """创建数据集相关活动 - 使用正确的活动类型"""
    try:
        if action == 'created':
            activity_type = ActivityType.DATASET_CREATED
            description = f'{user.username} 创建了数据集 "{dataset_name}"'
        elif action == 'updated':
            activity_type = ActivityType.DATASET_UPDATED
            description = f'{user.username} 更新了数据集 "{dataset_name}"'
        elif action == 'deleted':
            activity_type = ActivityType.DATASET_DELETED
            description = f'{user.username} 删除了数据集 "{dataset_name}"'
        else:
            activity_type = ActivityType.DATASET_CREATED
            description = f'{user.username} 操作了数据集 "{dataset_name}"'

        return create_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            resource_type='dataset',
            resource_id=dataset_id,
            resource_name=dataset_name
        )

    except Exception as e:
        print(f"❌ 创建数据集活动失败: {str(e)}")
        return None


def create_data_source_activity(user, data_source_name, data_source_id, action='created'):
    """创建数据源相关活动 - 使用正确的活动类型"""
    try:
        if action == 'created':
            activity_type = ActivityType.DATA_SOURCE_CREATED
            description = f'{user.username} 创建了数据源 "{data_source_name}"'
        elif action == 'updated':
            activity_type = ActivityType.DATA_SOURCE_UPDATED
            description = f'{user.username} 更新了数据源 "{data_source_name}"'
        elif action == 'deleted':
            activity_type = ActivityType.DATA_SOURCE_DELETED
            description = f'{user.username} 删除了数据源 "{data_source_name}"'
        else:
            activity_type = ActivityType.DATA_SOURCE_CREATED
            description = f'{user.username} 操作了数据源 "{data_source_name}"'

        return create_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            resource_type='data_source',
            resource_id=data_source_id,
            resource_name=data_source_name
        )

    except Exception as e:
        print(f"❌ 创建数据源活动失败: {str(e)}")
        return None


def create_visualization_activity(user, visualization_name, visualization_id, action='created'):
    """创建可视化相关活动 - 使用正确的活动类型"""
    try:
        if action == 'created':
            activity_type = ActivityType.VISUALIZATION_CREATED
            description = f'{user.username} 创建了可视化 "{visualization_name}"'
        elif action == 'updated':
            activity_type = ActivityType.VISUALIZATION_UPDATED
            description = f'{user.username} 更新了可视化 "{visualization_name}"'
        elif action == 'deleted':
            activity_type = ActivityType.VISUALIZATION_DELETED
            description = f'{user.username} 删除了可视化 "{visualization_name}"'
        else:
            activity_type = ActivityType.VISUALIZATION_CREATED
            description = f'{user.username} 操作了可视化 "{visualization_name}"'

        return create_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            resource_type='visualization',
            resource_id=visualization_id,
            resource_name=visualization_name
        )

    except Exception as e:
        print(f"❌ 创建可视化活动失败: {str(e)}")
        return None


def create_pipeline_activity(user, pipeline_name, pipeline_id, action='executed'):
    """创建处理流程相关活动 - 使用正确的活动类型"""
    try:
        if action == 'created':
            activity_type = ActivityType.PIPELINE_CREATED
            description = f'{user.username} 创建了处理流程 "{pipeline_name}"'
        elif action == 'executed':
            activity_type = ActivityType.PIPELINE_EXECUTED
            description = f'{user.username} 执行了处理流程 "{pipeline_name}"'
        elif action == 'deleted':
            activity_type = ActivityType.PIPELINE_DELETED
            description = f'{user.username} 删除了处理流程 "{pipeline_name}"'
        else:
            activity_type = ActivityType.PIPELINE_EXECUTED
            description = f'{user.username} 操作了处理流程 "{pipeline_name}"'

        return create_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            resource_type='pipeline',
            resource_id=pipeline_id,
            resource_name=pipeline_name
        )

    except Exception as e:
        print(f"❌ 创建处理流程活动失败: {str(e)}")
        return None


def create_ai_model_activity(user, model_name, model_id, action='trained'):
    """创建AI模型相关活动 - 使用正确的活动类型"""
    try:
        if action == 'trained':
            activity_type = ActivityType.AI_MODEL_TRAINED
            description = f'{user.username} 训练了AI模型 "{model_name}"'
        elif action == 'created':
            activity_type = ActivityType.AI_MODEL_CREATED
            description = f'{user.username} 创建了AI模型 "{model_name}"'
        elif action == 'deleted':
            activity_type = ActivityType.AI_MODEL_DELETED
            description = f'{user.username} 删除了AI模型 "{model_name}"'
        else:
            activity_type = ActivityType.AI_MODEL_TRAINED
            description = f'{user.username} 操作了AI模型 "{model_name}"'

        return create_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            resource_type='ai_model',
            resource_id=model_id,
            resource_name=model_name
        )

    except Exception as e:
        print(f"❌ 创建AI模型活动失败: {str(e)}")
        return None