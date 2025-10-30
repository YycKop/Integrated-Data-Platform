# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/services.py
from django.utils import timezone
from datetime import timedelta
from .models import Activity, ActivityType
import logging

logger = logging.getLogger(__name__)


class ActivityDataAggregator:
    """
    活动数据聚合服务 - 直接从各模块读取数据生成活动记录
    """

    @staticmethod
    def aggregate_recent_activities(days=30, limit=100):
        """
        聚合各模块的最近活动数据
        """
        try:
            all_activities = []

            # 1. 聚合数据源活动
            data_source_activities = ActivityDataAggregator._get_data_source_activities(days)
            all_activities.extend(data_source_activities)

            # 2. 聚合数据集活动
            dataset_activities = ActivityDataAggregator._get_dataset_activities(days)
            all_activities.extend(dataset_activities)

            # 3. 聚合处理流程活动
            pipeline_activities = ActivityDataAggregator._get_pipeline_activities(days)
            all_activities.extend(pipeline_activities)

            # 4. 聚合可视化活动
            visualization_activities = ActivityDataAggregator._get_visualization_activities(days)
            all_activities.extend(visualization_activities)

            # 5. 聚合看板活动
            dashboard_activities = ActivityDataAggregator._get_dashboard_activities(days)
            all_activities.extend(dashboard_activities)

            # 6. 聚合AI模型活动
            ai_model_activities = ActivityDataAggregator._get_ai_model_activities(days)
            all_activities.extend(ai_model_activities)

            # 按时间排序并限制数量
            all_activities.sort(key=lambda x: x['timestamp'], reverse=True)

            logger.info(f"✅ 成功聚合 {len(all_activities)} 条活动记录")
            return all_activities[:limit]

        except Exception as e:
            logger.error(f"❌ 聚合活动数据失败: {str(e)}")
            return []

    @staticmethod
    def _get_data_source_activities(days):
        """获取数据源相关活动 - 保持原有格式"""
        try:
            from datasets.models import DataSource  # 延迟导入避免循环依赖
            since_date = timezone.now() - timedelta(days=days)
            data_sources = DataSource.objects.filter(
                created_at__gte=since_date
            ).select_related('created_by')

            activities = []
            for data_source in data_sources:
                # 保持原有格式：用户 操作 结果名称
                description = f'{data_source.created_by.username} 创建了数据源 "{data_source.name}"'

                activities.append({
                    'id': f"ds_{data_source.id}",
                    'user': data_source.created_by,
                    'user_name': data_source.created_by.username,
                    'activity_type': ActivityType.DATA_SOURCE_CREATED,
                    'activity_type_display': '创建数据源',
                    'description': description,
                    'resource_type': 'data_source',
                    'resource_id': data_source.id,
                    'resource_name': data_source.name,
                    'timestamp': data_source.created_at,
                    'metadata': {
                        'data_source_type': data_source.type,
                        'source': 'direct_read'
                    }
                })

            logger.info(f"📊 读取到 {len(activities)} 个数据源活动")
            return activities
        except Exception as e:
            logger.error(f"获取数据源活动失败: {str(e)}")
            return []

    @staticmethod
    def _get_dataset_activities(days):
        """获取数据集相关活动 - 保持原有格式"""
        try:
            from datasets.models import Dataset  # 延迟导入避免循环依赖
            since_date = timezone.now() - timedelta(days=days)
            datasets = Dataset.objects.filter(
                created_at__gte=since_date
            ).select_related('created_by', 'data_source')

            activities = []
            for dataset in datasets:
                # 保持原有格式：用户 操作 结果名称
                description = f'{dataset.created_by.username} 创建了数据集 "{dataset.name}"'

                activities.append({
                    'id': f"dt_{dataset.id}",
                    'user': dataset.created_by,
                    'user_name': dataset.created_by.username,
                    'activity_type': ActivityType.DATASET_CREATED,
                    'activity_type_display': '创建数据集',
                    'description': description,
                    'resource_type': 'dataset',
                    'resource_id': dataset.id,
                    'resource_name': dataset.name,
                    'timestamp': dataset.created_at,
                    'metadata': {
                        'data_source': dataset.data_source.name if dataset.data_source else '未知',
                        'record_count': dataset.datarecord_set.count(),
                        'data_type': dataset.data_type,
                        'source': 'direct_read'
                    }
                })

            logger.info(f"📊 读取到 {len(activities)} 个数据集活动")
            return activities
        except Exception as e:
            logger.error(f"获取数据集活动失败: {str(e)}")
            return []

    @staticmethod
    def _get_pipeline_activities(days):
        """获取处理流程相关活动 - 保持原有格式"""
        try:
            from processing.models import ProcessingPipeline  # 延迟导入避免循环依赖
            since_date = timezone.now() - timedelta(days=days)
            pipelines = ProcessingPipeline.objects.filter(
                created_at__gte=since_date
            ).select_related('created_by')

            activities = []
            for pipeline in pipelines:
                # 根据状态确定操作动词
                action_verb = "创建了"
                activity_type = ActivityType.PIPELINE_EXECUTED
                activity_display = "创建处理流程"

                if pipeline.status == 'running':
                    action_verb = "执行了"
                    activity_type = ActivityType.PIPELINE_EXECUTED
                    activity_display = "执行处理流程"
                elif pipeline.status == 'completed':
                    action_verb = "完成了"
                    activity_type = ActivityType.PIPELINE_EXECUTED
                    activity_display = "完成处理流程"

                # 保持原有格式：用户 操作 结果名称
                description = f'{pipeline.created_by.username} {action_verb}处理流程 "{pipeline.name}"'

                activities.append({
                    'id': f"pp_{pipeline.id}",
                    'user': pipeline.created_by,
                    'user_name': pipeline.created_by.username,
                    'activity_type': activity_type,
                    'activity_type_display': activity_display,
                    'description': description,
                    'resource_type': 'pipeline',
                    'resource_id': pipeline.id,
                    'resource_name': pipeline.name,
                    'timestamp': pipeline.created_at,
                    'metadata': {
                        'status': pipeline.status,
                        'source': 'direct_read'
                    }
                })

            logger.info(f"📊 读取到 {len(activities)} 个处理流程活动")
            return activities
        except Exception as e:
            logger.error(f"获取处理流程活动失败: {str(e)}")
            return []

    @staticmethod
    def _get_visualization_activities(days):
        """获取可视化相关活动 - 保持原有格式"""
        try:
            from visualization.models import Visualization  # 延迟导入避免循环依赖
            since_date = timezone.now() - timedelta(days=days)
            visualizations = Visualization.objects.filter(
                created_at__gte=since_date
            ).select_related('created_by', 'chart_type', 'dataset')

            activities = []
            for viz in visualizations:
                # 保持原有格式：用户 操作 结果名称
                description = f'{viz.created_by.username} 创建了可视化 "{viz.name}"'

                activities.append({
                    'id': f"viz_{viz.id}",
                    'user': viz.created_by,
                    'user_name': viz.created_by.username,
                    'activity_type': ActivityType.VISUALIZATION_CREATED,
                    'activity_type_display': '创建可视化',
                    'description': description,
                    'resource_type': 'visualization',
                    'resource_id': viz.id,
                    'resource_name': viz.name,
                    'timestamp': viz.created_at,
                    'metadata': {
                        'chart_type': viz.chart_type.name,
                        'dataset': viz.dataset.name if viz.dataset else '未知',
                        'source': 'direct_read'
                    }
                })

            logger.info(f"📊 读取到 {len(activities)} 个可视化活动")
            return activities
        except Exception as e:
            logger.error(f"获取可视化活动失败: {str(e)}")
            return []

    @staticmethod
    def _get_dashboard_activities(days):
        """获取看板相关活动 - 保持原有格式"""
        try:
            from visualization.models import Dashboard  # 延迟导入避免循环依赖
            since_date = timezone.now() - timedelta(days=days)
            dashboards = Dashboard.objects.filter(
                created_at__gte=since_date
            ).select_related('created_by')

            activities = []
            for dashboard in dashboards:
                # 保持原有格式：用户 操作 结果名称
                description = f'{dashboard.created_by.username} 创建了看板 "{dashboard.name}"'

                activities.append({
                    'id': f"db_{dashboard.id}",
                    'user': dashboard.created_by,
                    'user_name': dashboard.created_by.username,
                    'activity_type': ActivityType.DASHBOARD_CREATED,
                    'activity_type_display': '创建看板',
                    'description': description,
                    'resource_type': 'dashboard',
                    'resource_id': dashboard.id,
                    'resource_name': dashboard.name,
                    'timestamp': dashboard.created_at,
                    'metadata': {
                        'chart_count': dashboard.dashboarditem_set.count(),
                        'is_public': dashboard.is_public,
                        'source': 'direct_read'
                    }
                })

            logger.info(f"📊 读取到 {len(activities)} 个看板活动")
            return activities
        except Exception as e:
            logger.error(f"获取看板活动失败: {str(e)}")
            return []

    @staticmethod
    def _get_ai_model_activities(days):
        """获取AI模型相关活动 - 保持原有格式"""
        try:
            from ai.models import AIModel  # 延迟导入避免循环依赖
            since_date = timezone.now() - timedelta(days=days)
            ai_models = AIModel.objects.filter(
                created_at__gte=since_date
            ).select_related('created_by')

            activities = []
            for model in ai_models:
                # 根据状态确定操作动词
                if model.status == 'trained' and hasattr(model, 'trained_at') and model.trained_at:
                    action_verb = "训练了"
                    activity_type = ActivityType.AI_MODEL_TRAINED
                    activity_display = "训练AI模型"
                    timestamp = model.trained_at
                else:
                    action_verb = "创建了"
                    activity_type = ActivityType.AI_MODEL_TRAINED
                    activity_display = "创建AI模型"
                    timestamp = model.created_at

                # 保持原有格式：用户 操作 结果名称
                description = f'{model.created_by.username} {action_verb}AI模型 "{model.name}"'

                activities.append({
                    'id': f"ai_{model.id}",
                    'user': model.created_by,
                    'user_name': model.created_by.username,
                    'activity_type': activity_type,
                    'activity_type_display': activity_display,
                    'description': description,
                    'resource_type': 'ai_model',
                    'resource_id': model.id,
                    'resource_name': model.name,
                    'timestamp': timestamp,
                    'metadata': {
                        'model_type': getattr(model, 'model_type', 'unknown'),
                        'status': model.status,
                        'accuracy': getattr(model, 'accuracy', None),
                        'source': 'direct_read'
                    }
                })

            logger.info(f"📊 读取到 {len(activities)} 个AI模型活动")
            return activities
        except Exception as e:
            logger.error(f"获取AI模型活动失败: {str(e)}")
            return []

    @staticmethod
    def sync_activities_to_database():
        """
        将聚合的活动数据同步到数据库
        用于修复缺失的活动记录
        """
        try:
            aggregated_activities = ActivityDataAggregator.aggregate_recent_activities(days=30)
            created_count = 0

            for agg_activity in aggregated_activities:
                # 检查是否已存在相同的活动记录
                existing = Activity.objects.filter(
                    user=agg_activity['user'],
                    activity_type=agg_activity['activity_type'],
                    resource_type=agg_activity['resource_type'],
                    resource_id=agg_activity['resource_id'],
                    created_at__date=agg_activity['timestamp'].date()
                ).exists()

                if not existing:
                    Activity.objects.create(
                        user=agg_activity['user'],
                        activity_type=agg_activity['activity_type'],
                        description=agg_activity['description'],
                        resource_type=agg_activity['resource_type'],
                        resource_id=agg_activity['resource_id'],
                        resource_name=agg_activity['resource_name'],
                        metadata=agg_activity['metadata'],
                        created_at=agg_activity['timestamp']
                    )
                    created_count += 1

            logger.info(f"✅ 成功同步 {created_count} 条活动记录到数据库")
            return created_count

        except Exception as e:
            logger.error(f"❌ 同步活动数据到数据库失败: {str(e)}")
            return 0