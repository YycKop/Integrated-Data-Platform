# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/ai/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db import transaction
from .models import AIModel, PredictionTask
from .serializers import (
    AIModelSerializer, PredictionTaskSerializer,
    TrainingRequestSerializer, PredictionRequestSerializer
)
from datasets.models import Dataset, DataRecord
from datasets.serializers import DatasetSerializer
from activities.utils import create_ai_model_activity
import logging

logger = logging.getLogger(__name__)


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可以编辑，其他认证用户只能查看"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # 所有认证用户都可以看到所有AI模型
        return AIModel.objects.all()

    def perform_create(self, serializer):
        ai_model = serializer.save(created_by=self.request.user)
        # 修复：创建AI模型活动记录
        create_ai_model_activity(
            user=self.request.user,
            model_name=ai_model.name,
            model_id=ai_model.id,
            action='created'
        )

    @action(detail=False, methods=['get'])
    def datasets(self, request):
        """获取可用于AI训练的数据集列表"""
        try:
            # 只返回用户有权限访问的数据集
            datasets = Dataset.objects.filter(created_by=request.user)
            print(f"找到的数据集数量: {datasets.count()}")

            serializer = DatasetSerializer(datasets, many=True)
            response_data = {
                'success': True,
                'data': serializer.data,
                'count': datasets.count()
            }
            print(f"返回的数据: {response_data}")
            return Response(response_data)
        except Exception as e:
            logger.error(f"获取数据集列表失败: {str(e)}")
            return Response({
                'success': False,
                'error': '获取数据集失败',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def dataset_columns(self, request):
        """获取数据集的列名"""
        try:
            dataset_id = request.query_params.get('dataset_id')
            if not dataset_id:
                return Response({
                    'success': False,
                    'error': '数据集ID不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)

            dataset = Dataset.objects.filter(
                id=dataset_id,
                created_by=request.user
            ).first()

            if not dataset:
                return Response({
                    'success': False,
                    'error': '数据集不存在或没有访问权限'
                }, status=status.HTTP_404_NOT_FOUND)

            # 获取数据集的列名
            columns = self._get_dataset_columns(dataset)

            return Response({
                'success': True,
                'columns': columns,
                'dataset_name': dataset.name,
                'record_count': dataset.datarecord_set.count()
            })

        except Exception as e:
            logger.error(f"获取数据集列名失败: {str(e)}")
            return Response({
                'success': False,
                'error': '获取列名失败',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def dataset_columns(self, request):
        """获取数据集的列名"""
        try:
            dataset_id = request.query_params.get('dataset_id')
            if not dataset_id:
                return Response({
                    'success': False,
                    'error': '数据集ID不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)

            dataset = Dataset.objects.filter(
                id=dataset_id,
                created_by=request.user
            ).first()

            if not dataset:
                return Response({
                    'success': False,
                    'error': '数据集不存在或没有访问权限'
                }, status=status.HTTP_404_NOT_FOUND)

            # 获取数据集的列名
            columns = self._get_dataset_columns(dataset)

            return Response({
                'success': True,
                'columns': columns,
                'dataset_name': dataset.name,
                'record_count': dataset.datarecord_set.count()
            })

        except Exception as e:
            logger.error(f"获取数据集列名失败: {str(e)}")
            return Response({
                'success': False,
                'error': '获取列名失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_dataset_columns(self, dataset):
        """从数据集中提取列名"""
        try:
            # 方法1: 从数据记录中提取列名
            records = DataRecord.objects.filter(dataset=dataset)[:10]  # 取前10条记录
            if records:
                all_columns = set()
                for record in records:
                    if record.data:
                        all_columns.update(record.data.keys())
                columns = list(all_columns)
                print(f"从记录中提取的列名: {columns}")  # 调试信息
                return columns

            # 方法2: 如果数据集有预定义的列信息
            if hasattr(dataset, 'columns') and dataset.columns:
                print(f"使用预定义列名: {dataset.columns}")  # 调试信息
                return dataset.columns

            print("没有找到列名")  # 调试信息
            return []

        except Exception as e:
            logger.error(f"提取数据集列名失败: {str(e)}")
            return []

    @action(detail=False, methods=['get'])
    def dataset_preview(self, request):
        """获取数据集预览数据"""
        try:
            dataset_id = request.query_params.get('dataset_id')
            if not dataset_id:
                return Response({
                    'success': False,
                    'error': '数据集ID不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)

            dataset = Dataset.objects.filter(
                id=dataset_id,
                created_by=request.user
            ).first()

            if not dataset:
                return Response({
                    'success': False,
                    'error': '数据集不存在或没有访问权限'
                }, status=status.HTTP_404_NOT_FOUND)

            # 获取前20条记录作为预览
            records = DataRecord.objects.filter(dataset=dataset)[:20]
            preview_data = []

            for record in records:
                preview_data.append(record.data)

            return Response({
                'success': True,
                'data': preview_data,
                'total_records': dataset.datarecord_set.count(),
                'dataset_name': dataset.name
            })

        except Exception as e:
            logger.error(f"获取数据集预览失败: {str(e)}")
            return Response({
                'success': False,
                'error': '获取预览数据失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def train(self, request, pk=None):
        """训练AI模型"""
        try:
            ai_model = self.get_object()
            serializer = TrainingRequestSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 开始训练任务
            task = PredictionTask.objects.create(
                name=f"训练模型 - {ai_model.name}",
                task_type='model_training',
                ai_model=ai_model,
                input_parameters=serializer.validated_data,
                created_by=request.user,
                status='running'
            )

            # 这里应该调用实际的AI训练服务
            # 暂时返回模拟结果
            result = {
                'success': True,
                'accuracy': 0.85,
                'model_path': f'ai_models/model_{ai_model.id}.pkl'
            }

            if result['success']:
                ai_model.status = 'active'
                ai_model.accuracy = result.get('accuracy')
                ai_model.model_file = result.get('model_path')
                ai_model.save()

                task.status = 'completed'
                task.output_result = result
                task.progress = 100

                # 修复：创建AI模型训练活动记录
                create_ai_model_activity(
                    user=request.user,
                    model_name=ai_model.name,
                    model_id=ai_model.id,
                    action='trained'
                )
            else:
                task.status = 'failed'
                task.error_message = result.get('error')

            task.save()

            return Response({
                'success': True,
                'task_id': task.id,
                'result': result
            })

        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@action(detail=True, methods=['post'])


def predict(self, request, pk=None):
    """使用模型进行预测"""
    try:
        ai_model = self.get_object()
        serializer = PredictionRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 创建预测任务
        task = PredictionTask.objects.create(
            name=f"预测 - {ai_model.name}",
            task_type='batch_prediction',
            ai_model=ai_model,
            input_parameters=serializer.validated_data,
            created_by=request.user,
            status='running'
        )

        # 执行预测 - 这里应该调用实际的AI预测服务
        # 暂时返回模拟结果
        result = {
            'success': True,
            'predictions': [
                {'predicted_price': 25.5, 'confidence': 0.92},
                {'predicted_price': 28.3, 'confidence': 0.88}
            ]
        }

        if result['success']:
            task.status = 'completed'
            task.output_result = result
            task.progress = 100
        else:
            task.status = 'failed'
            task.error_message = result.get('error')

        task.save()

        return Response({
            'success': True,
            'task_id': task.id,
            'predictions': result.get('predictions', [])
        })

    except Exception as e:
        logger.error(f"预测失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@action(detail=True, methods=['post'])
def update_status(self, request, pk=None):
    """更新模型状态"""
    try:
        model = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(AIModel.STATUS_CHOICES):
            return Response({
                'success': False,
                'error': f'无效的状态: {new_status}'
            }, status=status.HTTP_400_BAD_REQUEST)

        model.status = new_status
        model.save()

        return Response({
            'success': True,
            'message': f'模型状态已更新为 {model.get_status_display()}',
            'status': model.status,
            'status_display': model.get_status_display()
        })

    except Exception as e:
        logger.error(f"更新模型状态失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@action(detail=True, methods=['post'])
def start_training(self, request, pk=None):
    """开始训练模型"""
    try:
        model = self.get_object()

        # 更新模型状态为训练中
        model.status = 'training'
        model.save()

        # 这里可以调用实际的训练服务
        # training_service.train_model(model, request.data)

        return Response({
            'success': True,
            'message': '模型训练已开始',
            'status': model.status,
            'status_display': model.get_status_display()
        })

    except Exception as e:
        logger.error(f"开始训练失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@action(detail=True, methods=['post'])
def complete_training(self, request, pk=None):
    """完成模型训练"""
    try:
        model = self.get_object()

        # 更新模型状态和准确率
        model.status = 'active'
        model.accuracy = request.data.get('accuracy', 0.85)  # 模拟准确率
        model.save()

        return Response({
            'success': True,
            'message': '模型训练完成',
            'status': model.status,
            'accuracy': model.accuracy,
            'status_display': model.get_status_display()
        })

    except Exception as e:
        logger.error(f"完成训练失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PredictionTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """预测任务视图集 - 所有认证用户都可以查看"""
    queryset = PredictionTask.objects.all()
    serializer_class = PredictionTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 所有认证用户都可以看到所有预测任务
        return PredictionTask.objects.all()


# 确保这些函数存在
@api_view(['POST'])
def analyze_market_trends(request):
    """分析市场趋势"""
    try:
        # 这里应该调用实际的AI分析服务
        # 暂时返回模拟结果
        result = {
            'success': True,
            'trends': [
                {'period': '2024-01', 'trend': 'up', 'confidence': 0.85},
                {'period': '2024-02', 'trend': 'stable', 'confidence': 0.78}
            ],
            'insights': '市场价格呈现稳定上涨趋势'
        }
        return Response(result)
    except Exception as e:
        logger.error(f"市场趋势分析失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_insights(request):
    """生成数据洞察"""
    try:
        # 这里应该调用实际的AI洞察生成服务
        # 暂时返回模拟结果
        result = {
            'success': True,
            'insights': [
                '价格与季节性因素强相关',
                '产量增加会导致价格下降',
                '市场需求在Q4达到峰值'
            ],
            'recommendations': [
                '建议在Q3增加库存',
                '考虑多元化种植降低风险'
            ]
        }
        return Response(result)
    except Exception as e:
        logger.error(f"生成洞察失败: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
