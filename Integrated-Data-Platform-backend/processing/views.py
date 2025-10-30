# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/processing/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.exceptions import ValidationError
import pandas as pd
import logging

from .models import ProcessingPipeline, PipelineModule
from .serializers import ProcessingPipelineSerializer
from datasets.models import Dataset, DataRecord

from users.permissions import IsCreatorOrAdmin, IsAdminOrAnalyst
# 导入活动记录功能
from activities.utils import create_pipeline_activity

logger = logging.getLogger(__name__)


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可以编辑，其他认证用户只能查看"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrAnalyst(permissions.BasePermission):
    """管理员和数据分析师可以编辑"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'analyst']


class ProcessingPipelineViewSet(viewsets.ModelViewSet):
    queryset = ProcessingPipeline.objects.all()
    serializer_class = ProcessingPipelineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 所有认证用户都可以看到所有处理流程
        return ProcessingPipeline.objects.all()

    def get_permissions(self):
        if self.request.method in ['GET', 'execute']:
            # 查看和执行操作对所有认证用户开放
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'POST':
            # 创建操作需要管理员或数据分析师权限
            return [permissions.IsAuthenticated(), IsAdminOrAnalyst()]
        elif self.request.method in ['PUT', 'PATCH']:
            # 更新操作需要创建者或管理员权限
            return [permissions.IsAuthenticated(), IsCreatorOrAdmin()]
        elif self.request.method == 'DELETE':
            # 删除操作需要创建者或管理员权限
            return [permissions.IsAuthenticated(), IsCreatorOrAdmin()]

    def perform_create(self, serializer):
        try:
            pipeline = serializer.save(created_by=self.request.user)
            # 创建处理流程活动记录 - 修复调用
            from activities.utils import create_pipeline_activity
            result = create_pipeline_activity(
                user=self.request.user,
                pipeline_name=pipeline.name,
                pipeline_id=pipeline.id,
                action='created'
            )

            if result:
                print(f"✅ 处理流程活动记录创建成功: {result.description}")
            else:
                print(f"❌ 处理流程活动记录创建失败")

        except Exception as e:
            logger.error(f"创建处理流程失败: {str(e)}")
            logger.error(f"详细错误: {e.__class__.__name__}")
            if hasattr(e, 'detail'):
                logger.error(f"验证错误详情: {e.detail}")
            raise

    def perform_destroy(self, instance):
        # 检查权限：只有创建者或管理员可以删除
        if instance.created_by != self.request.user and self.request.user.role != 'admin':
            raise permissions.PermissionDenied("您只能删除自己创建的处理流程")
        super().perform_destroy(instance)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """执行处理流程"""
        try:
            pipeline = self.get_object()

            if not pipeline.input_dataset:
                return Response(
                    {'error': '输入数据集未设置'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            input_records = DataRecord.objects.filter(dataset=pipeline.input_dataset)

            if not input_records.exists():
                return Response(
                    {'error': '输入数据集为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 将记录转换为DataFrame
            data = []
            for record in input_records:
                data.append(record.data)

            df = pd.DataFrame(data)

            # 验证数据
            self.validate_pipeline_data(pipeline, df)

            # 记录原始数据条数
            original_count = len(df)

            # 按顺序执行处理模块
            pipeline_modules = PipelineModule.objects.filter(
                pipeline=pipeline
            ).order_by('order')

            execution_log = []

            for pipeline_module in pipeline_modules:
                before_count = len(df)

                # 根据模块类型执行不同的处理
                if pipeline_module.type == 'filter':
                    df = self._apply_filter(df, pipeline_module.configuration)
                elif pipeline_module.type == 'transform':
                    df = self._apply_transform(df, pipeline_module.configuration)
                elif pipeline_module.type == 'aggregate':
                    df = self._apply_aggregate(df, pipeline_module.configuration)
                elif pipeline_module.type == 'clean':
                    df = self._apply_clean(df, pipeline_module.configuration)
                elif pipeline_module.type == 'select':
                    df = self._apply_select(df, pipeline_module.configuration)
                elif pipeline_module.type == 'sort':
                    df = self._apply_sort(df, pipeline_module.configuration)

                # 记录执行结果
                after_count = len(df)
                execution_log.append({
                    'module': pipeline_module.name,
                    'type': pipeline_module.type,
                    'before_count': before_count,
                    'after_count': after_count,
                    'records_affected': before_count - after_count
                })

            # 处理输出数据集
            with transaction.atomic():
                output_dataset = pipeline.output_dataset

                if not output_dataset:
                    output_dataset_name = pipeline.output_dataset_name or f"{pipeline.name}_输出"

                    # 使用输入数据集的数据源，或者创建一个虚拟的数据源
                    input_dataset = pipeline.input_dataset
                    data_source = input_dataset.data_source if input_dataset.data_source else None

                    if not data_source:
                        from datasets.models import DataSource
                        data_source, created = DataSource.objects.get_or_create(
                            name="处理流程数据源",
                            type='manual',
                            defaults={
                                'description': '由数据处理流程自动创建的数据源',
                                'created_by': self.request.user
                            }
                        )

                    # 根据输出数据类型创建数据集
                    output_dataset = Dataset.objects.create(
                        name=output_dataset_name,
                        description=f"由处理流程 {pipeline.name} 生成",
                        data_source=data_source,
                        # 使用现有的 data_type 字段
                        data_type=pipeline.output_data_type,
                        data_structure={},  # 可以根据需要设置数据结构
                        created_by=self.request.user
                    )
                    pipeline.output_dataset = output_dataset
                    pipeline.save()

                # 清空输出数据集的现有记录
                DataRecord.objects.filter(dataset=output_dataset).delete()

                # 保存新记录
                records_created = 0
                for _, row in df.iterrows():
                    DataRecord.objects.create(
                        dataset=output_dataset,
                        data=row.to_dict()
                    )
                    records_created += 1

            # 创建处理流程执行活动记录
            create_pipeline_activity(
                user=self.request.user,
                pipeline_name=pipeline.name,
                pipeline_id=pipeline.id,
                action='executed'
            )

            logger.info(f"Pipeline {pipeline.name} executed successfully. "
                        f"Processed {original_count} -> {records_created} records")

            return Response({
                'message': '处理流程执行成功',
                'original_records': original_count,
                'processed_records': records_created,
                'output_dataset': output_dataset.name,
                'output_dataset_id': output_dataset.id,
                'output_data_type': output_dataset.data_type,
                'execution_log': execution_log
            })

        except ValidationError as e:
            logger.error(f"Pipeline validation error: {str(e)}")
            return Response(
                {'error': f'数据验证失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Pipeline execution error: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return Response(
                {'error': f'处理流程执行失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _apply_filter(self, df, config):
        """应用数据过滤"""
        field = config.get('field', '')
        operator = config.get('operator', '')
        value = config.get('value', '')

        if not field or field not in df.columns or not operator:
            return df

        try:
            if operator in ['>', '>=', '<', '<=']:
                df[field] = pd.to_numeric(df[field], errors='coerce')
                value = float(value)

            if operator == '==':
                return df[df[field] == value]
            elif operator == '!=':
                return df[df[field] != value]
            elif operator == '>':
                return df[df[field] > value]
            elif operator == '>=':
                return df[df[field] >= value]
            elif operator == '<':
                return df[df[field] < value]
            elif operator == '<=':
                return df[df[field] <= value]
            elif operator == 'contains':
                return df[df[field].astype(str).str.contains(str(value), na=False)]
            elif operator == 'not_contains':
                return df[~df[field].astype(str).str.contains(str(value), na=False)]
            elif operator == 'in':
                value_list = [v.strip() for v in str(value).split(',')]
                return df[df[field].isin(value_list)]
            elif operator == 'not_in':
                value_list = [v.strip() for v in str(value).split(',')]
                return df[~df[field].isin(value_list)]
            elif operator == 'is_null':
                return df[df[field].isna()]
            elif operator == 'not_null':
                return df[df[field].notna()]
            else:
                return df

        except Exception as e:
            logger.warning(f"Filter operation failed: {str(e)}")
            return df

    def _apply_transform(self, df, config):
        """应用数据转换 - 支持多字段"""
        fields = config.get('fields', [])
        operation = config.get('operation', '')
        new_field_prefix = config.get('new_field_prefix', '')
        time_format = config.get('time_format', 'auto')
        decimal_places = config.get('decimal_places', 2)

        # 兼容旧版本的单字段配置
        if not fields and 'field' in config:
            fields = [config.get('field', '')]
            new_field = config.get('new_field', '')
            if new_field and len(fields) == 1:
                new_field_prefix = new_field

        if not fields or not operation:
            return df

        try:
            # 处理每个选中的字段
            for field in fields:
                if field not in df.columns:
                    logger.warning(f"字段 '{field}' 在数据集中不存在，跳过")
                    continue

                # 确定目标字段名
                if new_field_prefix:
                    target_field = f"{new_field_prefix}_{field}"
                else:
                    target_field = field  # 覆盖原字段

                if operation == 'uppercase':
                    df[target_field] = df[field].astype(str).str.upper()
                elif operation == 'lowercase':
                    df[target_field] = df[field].astype(str).str.lower()
                elif operation == 'trim':
                    df[target_field] = df[field].astype(str).str.strip()
                elif operation == 'round':
                    df[target_field] = pd.to_numeric(df[field], errors='coerce').round(decimal_places)
                elif operation == 'abs':
                    df[target_field] = pd.to_numeric(df[field], errors='coerce').abs()
                elif operation == 'standardize':
                    mean = pd.to_numeric(df[field], errors='coerce').mean()
                    std = pd.to_numeric(df[field], errors='coerce').std()
                    df[target_field] = (pd.to_numeric(df[field], errors='coerce') - mean) / std
                elif operation == 'normalize':
                    min_val = pd.to_numeric(df[field], errors='coerce').min()
                    max_val = pd.to_numeric(df[field], errors='coerce').max()
                    df[target_field] = (pd.to_numeric(df[field], errors='coerce') - min_val) / (max_val - min_val)

                # 添加百分比转换操作
                elif operation == 'percent_to_decimal':
                    df[target_field] = self._convert_percent_to_decimal(df[field], decimal_places)
                elif operation == 'decimal_to_percent':
                    df[target_field] = self._convert_decimal_to_percent(df[field], decimal_places)

                # 时间数据提取操作
                elif operation.startswith('extract_'):
                    df[target_field] = self._extract_time_component(df[field], operation, time_format)

            return df
        except Exception as e:
            logger.warning(f"Transform operation failed: {str(e)}")
            return df

    def _convert_percent_to_decimal(self, series, decimal_places=2):
        """将百分比字符串转换为小数"""
        try:
            # 处理各种百分比格式：50%, 50.5%, 50.55% 等
            def convert_value(value):
                if pd.isna(value):
                    return value

                str_value = str(value).strip()

                # 移除百分号
                str_value = str_value.replace('%', '')

                # 转换为浮点数
                try:
                    numeric_value = float(str_value)
                    # 除以100得到小数
                    decimal_value = numeric_value / 100.0
                    # 四舍五入到指定小数位数
                    return round(decimal_value, decimal_places)
                except (ValueError, TypeError):
                    return value

            return series.apply(convert_value)
        except Exception as e:
            logger.warning(f"Percent to decimal conversion failed: {str(e)}")
            return series

    def _convert_decimal_to_percent(self, series, decimal_places=2):
        """将小数转换为百分比"""
        try:
            def convert_value(value):
                if pd.isna(value):
                    return value

                try:
                    # 转换为浮点数
                    numeric_value = float(value)
                    # 乘以100得到百分比
                    percent_value = numeric_value * 100.0
                    # 四舍五入到指定小数位数
                    rounded_value = round(percent_value, decimal_places)
                    return rounded_value
                except (ValueError, TypeError):
                    return value

            return series.apply(convert_value)
        except Exception as e:
            logger.warning(f"Decimal to percent conversion failed: {str(e)}")
            return series

    def _extract_time_component(self, series, operation, time_format='auto'):
        """提取时间组件"""
        try:
            # 将系列转换为字符串类型
            str_series = series.astype(str)

            # 根据时间格式解析日期时间
            if time_format == 'auto':
                # 尝试自动解析常见格式
                parsed_dates = pd.to_datetime(str_series, errors='coerce', infer_datetime_format=True)
            else:
                # 根据指定格式解析
                format_mapping = {
                    'YYYYmmdd': '%Y%m%d',
                    'YYYY-mm-dd': '%Y-%m-%d',
                    'YYYY/mm/dd': '%Y/%m/%d',
                    'YYYY年mm月dd日': '%Y年%m月%d日',
                    'hhMMss': '%H%M%S',
                    'hh:MM:ss': '%H:%M:%S',
                    'hh时MM分ss秒': '%H时%M分%S秒',
                    'YYYYmmdd hhMMss': '%Y%m%d %H%M%S',
                    'YYYY-mm-dd hh:MM:ss': '%Y-%m-%d %H:%M:%S',
                    'timestamp': 'timestamp'  # 特殊处理时间戳
                }

                if time_format == 'timestamp':
                    # 处理时间戳（假设是秒级或毫秒级）
                    numeric_series = pd.to_numeric(series, errors='coerce')
                    # 判断是秒级还是毫秒级时间戳
                    if numeric_series.max() > 1e10:  # 大于 1e10 可能是毫秒级
                        parsed_dates = pd.to_datetime(numeric_series, unit='ms', errors='coerce')
                    else:
                        parsed_dates = pd.to_datetime(numeric_series, unit='s', errors='coerce')
                else:
                    pandas_format = format_mapping.get(time_format, None)
                    if pandas_format:
                        parsed_dates = pd.to_datetime(str_series, format=pandas_format, errors='coerce')
                    else:
                        parsed_dates = pd.to_datetime(str_series, errors='coerce')

            # 根据操作类型提取不同的时间组件
            if operation == 'extract_year':
                return parsed_dates.dt.year
            elif operation == 'extract_month':
                return parsed_dates.dt.month
            elif operation == 'extract_day':
                return parsed_dates.dt.day
            elif operation == 'extract_hour':
                return parsed_dates.dt.hour
            elif operation == 'extract_minute':
                return parsed_dates.dt.minute
            elif operation == 'extract_second':
                return parsed_dates.dt.second
            elif operation == 'extract_quarter':
                return parsed_dates.dt.quarter
            elif operation == 'extract_weekday':
                # 返回星期几 (0-6, 0=周一)
                return parsed_dates.dt.dayofweek
            else:
                return series

        except Exception as e:
            logger.warning(f"Time extraction failed: {str(e)}")
            return series

    def _apply_aggregate(self, df, config):
        """应用数据聚合 - 支持多字段分组和多字段聚合"""
        # 兼容旧版本配置（单个字段分组和聚合）
        if 'group_by' in config and isinstance(config['group_by'], str) and config['group_by']:
            # 转换为新格式
            old_group_by = config['group_by']
            old_aggregate_field = config.get('aggregate_field', '')
            old_operation = config.get('operation', '')

            if old_aggregate_field and old_operation:
                config['group_by'] = [old_group_by]
                config['aggregations'] = [{
                    'field': old_aggregate_field,
                    'operation': old_operation,
                    'output_name': f"{old_aggregate_field}_{old_operation}"
                }]

        group_by = config.get('group_by', [])
        aggregations = config.get('aggregations', [])

        # 确保 group_by 是列表
        if isinstance(group_by, str):
            group_by = [group_by] if group_by else []

        # 确保 aggregations 是列表
        if isinstance(aggregations, dict):
            aggregations = [aggregations]

        # 验证配置
        if not group_by:
            logger.warning("聚合操作缺少分组字段")
            return df

        if not aggregations:
            logger.warning("聚合操作缺少聚合配置")
            return df

        # 验证分组字段是否存在
        for field in group_by:
            if field not in df.columns:
                logger.warning(f"分组字段 '{field}' 在数据集中不存在")
                return df

        try:
            # 构建聚合配置字典
            agg_dict = {}
            output_columns = list(group_by)  # 保留分组字段

            for agg_config in aggregations:
                field = agg_config.get('field', '')
                operation = agg_config.get('operation', '')
                output_name = agg_config.get('output_name', '')

                if not field or not operation:
                    continue

                if field not in df.columns:
                    logger.warning(f"聚合字段 '{field}' 在数据集中不存在")
                    continue

                # 转换数值类型
                if operation != 'count':  # count 不需要数值转换
                    df[field] = pd.to_numeric(df[field], errors='coerce')

                # 设置默认输出名称
                if not output_name:
                    operation_names = {
                        'sum': '总和',
                        'mean': '平均值',
                        'count': '计数',
                        'max': '最大值',
                        'min': '最小值',
                        'std': '标准差',
                        'var': '方差',
                        'median': '中位数',
                        'first': '第一个值',
                        'last': '最后一个值'
                    }
                    output_name = f"{field}_{operation_names.get(operation, operation)}"

                # 映射操作到pandas函数
                operation_mapping = {
                    'sum': 'sum',
                    'mean': 'mean',
                    'count': 'count',
                    'max': 'max',
                    'min': 'min',
                    'std': 'std',
                    'var': 'var',
                    'median': 'median',
                    'first': 'first',
                    'last': 'last'
                }

                pandas_operation = operation_mapping.get(operation)
                if pandas_operation:
                    agg_dict[output_name] = (field, pandas_operation)
                    output_columns.append(output_name)

            if not agg_dict:
                logger.warning("没有有效的聚合配置")
                return df

            # 执行分组聚合
            grouped = df.groupby(group_by)

            # 构建聚合表达式
            agg_expressions = {}
            for output_name, (field, operation) in agg_dict.items():
                if operation == 'first':
                    agg_expressions[output_name] = grouped[field].first()
                elif operation == 'last':
                    agg_expressions[output_name] = grouped[field].last()
                else:
                    agg_expressions[output_name] = getattr(grouped[field], operation)()

            # 执行聚合
            result = pd.DataFrame(agg_expressions).reset_index()

            # 确保列顺序正确
            result = result[output_columns]

            logger.info(f"聚合操作完成: 分组字段={group_by}, 聚合配置={len(aggregations)}个")
            return result

        except Exception as e:
            logger.error(f"Aggregate operation failed: {str(e)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return df

    def _apply_select(self, df, config):
        """应用数据截取 - 选择特定字段"""
        selected_fields = config.get('selected_fields', [])
        mode = config.get('mode', 'include')  # include 或 exclude
        rename_mapping = config.get('rename_mapping', {})

        if not selected_fields:
            logger.warning("数据截取操作未选择任何字段")
            return df

        try:
            # 根据模式处理字段选择
            if mode == 'include':
                # 只保留选中的字段
                # 确保选中的字段在数据集中存在
                existing_fields = [field for field in selected_fields if field in df.columns]
                if not existing_fields:
                    logger.warning("选中的字段在数据集中都不存在")
                    return df
                result_df = df[existing_fields].copy()
            elif mode == 'exclude':
                # 排除选中的字段
                # 确保排除后还有字段剩余
                remaining_fields = [field for field in df.columns if field not in selected_fields]
                if not remaining_fields:
                    logger.warning("排除所有字段后没有剩余字段")
                    return df
                result_df = df[remaining_fields].copy()
            else:
                logger.warning(f"未知的数据截取模式: {mode}")
                return df

            # 应用字段重命名
            if rename_mapping:
                rename_dict = {}
                for old_name, new_name in rename_mapping.items():
                    if old_name in result_df.columns and new_name and new_name.strip():
                        rename_dict[old_name] = new_name.strip()

                if rename_dict:
                    result_df = result_df.rename(columns=rename_dict)
                    logger.info(f"重命名字段: {rename_dict}")

            logger.info(f"数据截取完成: 模式={mode}, 字段数={len(result_df.columns)}")
            return result_df

        except Exception as e:
            logger.error(f"数据截取操作失败: {str(e)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return df

    def _apply_clean(self, df, config):
        """应用数据清洗"""
        field = config.get('field', '')
        operation = config.get('operation', '')
        value = config.get('value', '')

        if not field or field not in df.columns:
            return df

        try:
            if operation == 'fill_na':
                fill_value = value if value != '' else 0
                df[field] = df[field].fillna(fill_value)
            elif operation == 'remove_duplicates':
                df = df.drop_duplicates(subset=[field])
            elif operation == 'remove_na':
                df = df.dropna(subset=[field])

            return df
        except Exception as e:
            logger.warning(f"Clean operation failed: {str(e)}")
            return df

    def validate_pipeline_data(self, pipeline, df):
        """验证管道数据 - 支持动态生成的字段"""
        if df.empty:
            raise ValidationError("输入数据集为空")

        pipeline_modules = PipelineModule.objects.filter(pipeline=pipeline).order_by('order')

        # 模拟执行流程来构建动态字段列表
        current_df = df.copy()
        available_columns = set(current_df.columns)

        for pipeline_module in pipeline_modules:
            config = pipeline_module.configuration

            if pipeline_module.type in ['filter', 'transform', 'clean']:
                field = config.get('field', '')
                if field and field not in available_columns:
                    raise ValidationError(f"字段 '{field}' 在数据集中不存在")

            elif pipeline_module.type == 'aggregate':
                group_by = config.get('group_by', [])
                aggregations = config.get('aggregations', [])

                # 确保 group_by 是列表
                if isinstance(group_by, str):
                    group_by = [group_by] if group_by else []

                # 确保 aggregations 是列表
                if isinstance(aggregations, dict):
                    aggregations = [aggregations]

                # 验证分组字段
                for field in group_by:
                    if field and field not in available_columns:
                        raise ValidationError(f"分组字段 '{field}' 在数据集中不存在")

                # 验证聚合字段
                for agg_config in aggregations:
                    field = agg_config.get('field', '')
                    if field and field not in available_columns:
                        raise ValidationError(f"聚合字段 '{field}' 在数据集中不存在")

            elif pipeline_module.type == 'select':
                selected_fields = config.get('selected_fields', [])
                mode = config.get('mode', 'include')

                if not selected_fields:
                    raise ValidationError("数据截取模块必须选择至少一个字段")

                # 验证选中的字段是否存在
                if mode == 'include':
                    for field in selected_fields:
                        if field and field not in available_columns:
                            raise ValidationError(f"数据截取字段 '{field}' 在数据集中不存在")

            elif pipeline_module.type == 'sort':

                sort_fields = config.get('sort_fields', [])

                if not sort_fields:
                    raise ValidationError("排序模块必须配置至少一个排序条件")

                # 验证排序字段是否存在

                for sort_config in sort_fields:

                    field = sort_config.get('field', '')

                    if field and field not in available_columns:
                        raise ValidationError(f"排序字段 '{field}' 在数据集中不存在")

                # 验证截取配置

                enable_limit = config.get('enable_limit', False)

                if enable_limit:

                    limit_type = config.get('limit_type', 'top')

                    if limit_type in ['top', 'bottom']:

                        limit_count = config.get('limit_count', 10)

                        if limit_count <= 0:
                            raise ValidationError("截取行数必须大于0")


                    elif limit_type == 'range':

                        start_row = config.get('start_row', 0)

                        end_row = config.get('end_row', 10)

                        if start_row < 0:
                            raise ValidationError("起始行不能为负数")

                        if start_row >= end_row:
                            raise ValidationError("起始行必须小于结束行")

                    else:

                        raise ValidationError(f"未知的截取类型: {limit_type}")
            # 模拟执行当前模块，更新可用字段列表
            try:
                if pipeline_module.type == 'filter':
                    current_df = self._apply_filter(current_df, config)
                elif pipeline_module.type == 'transform':
                    current_df = self._apply_transform(current_df, config)
                    # 更新可用字段列表
                    fields = config.get('fields', [])
                    new_field_prefix = config.get('new_field_prefix', '')
                    if new_field_prefix and fields:
                        for field in fields:
                            new_field = f"{new_field_prefix}_{field}"
                            if new_field not in available_columns:
                                available_columns.add(new_field)
                elif pipeline_module.type == 'aggregate':
                    current_df = self._apply_aggregate(current_df, config)
                    available_columns.clear()
                    if not current_df.empty:
                        available_columns.update(current_df.columns.tolist())
                elif pipeline_module.type == 'clean':
                    current_df = self._apply_clean(current_df, config)
                elif pipeline_module.type == 'select':
                    current_df = self._apply_select(current_df, config)
                    available_columns.clear()
                    if not current_df.empty:
                        available_columns.update(current_df.columns.tolist())
                elif pipeline_module.type == 'sort':
                    current_df = self._apply_sort(current_df, config)
                    # 排序不改变字段结构，但需要更新可用字段列表（字段顺序可能改变）
                    available_columns.clear()
                    if not current_df.empty:
                        available_columns.update(current_df.columns.tolist())
            except Exception as e:
                logger.debug(f"模拟执行模块时发生错误（在验证阶段可忽略）: {str(e)}")
                continue
