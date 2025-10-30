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
        # 验证活动类型是否有效
        valid_types = [choice[0] for choice in ActivityType.choices]
        if activity_type not in valid_types:
            print(f"⚠️ 警告: 活动类型 '{activity_type}' 不在有效类型中")
            # 使用默认类型
            activity_type = ActivityType.DATASET_CREATED

        activity = Activity.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            metadata=metadata or {}
        )
        print(f"✅ 成功创建活动记录: {description}")
        return activity
    except Exception as e:
        print(f"❌ 创建活动记录失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return None


# 具体的活动创建函数
def create_data_source_activity(user, data_source_name, data_source_id, action='created'):
    """创建数据源相关活动"""
    if action == 'created':
        activity_type = ActivityType.DATA_SOURCE_CREATED
        description = f'创建了数据源 "{data_source_name}"'

    return create_activity(
        user=user,
        activity_type=activity_type,
        description=description,
        resource_type='data_source',
        resource_id=data_source_id,
        resource_name=data_source_name
    )


def create_dataset_activity(user, dataset_name, dataset_id, action='created'):
    """创建数据集相关活动"""
    if action == 'created':
        activity_type = ActivityType.DATASET_CREATED
        description = f'创建了数据集 "{dataset_name}"'

    return create_activity(
        user=user,
        activity_type=activity_type,
        description=description,
        resource_type='dataset',
        resource_id=dataset_id,
        resource_name=dataset_name
    )


def create_pipeline_activity(user, pipeline_name, pipeline_id, action='executed'):
    """创建处理流程相关活动"""
    if action == 'created':
        activity_type = ActivityType.PIPELINE_EXECUTED
        description = f'创建了处理流程 "{pipeline_name}"'
    elif action == 'executed':
        activity_type = ActivityType.PIPELINE_EXECUTED
        description = f'执行了处理流程 "{pipeline_name}"'

    return create_activity(
        user=user,
        activity_type=activity_type,
        description=description,
        resource_type='pipeline',
        resource_id=pipeline_id,
        resource_name=pipeline_name
    )


def create_dashboard_activity(user, dashboard_name, dashboard_id, action='created'):
    """创建看板相关活动"""
    if action == 'created':
        activity_type = ActivityType.DASHBOARD_CREATED
        description = f'创建了数据看板 "{dashboard_name}"'
    elif action == 'updated':
        activity_type = ActivityType.DASHBOARD_CREATED
        description = f'更新了数据看板 "{dashboard_name}"'

    return create_activity(
        user=user,
        activity_type=activity_type,
        description=description,
        resource_type='dashboard',
        resource_id=dashboard_id,
        resource_name=dashboard_name
    )