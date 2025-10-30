# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/datasets/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
import json
import pandas as pd
from io import StringIO, BytesIO

# 确保正确导入 DatabaseConnector
from .models import DataSource, Dataset, DataRecord
from .serializers import DataSourceSerializer, DatasetSerializer, DataRecordSerializer
from .db_utils import DatabaseConnector

# 导入活动记录功能
from activities.utils import create_dataset_activity, create_data_source_activity


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可以编辑，其他认证用户只能查看"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # 所有认证用户都可以看到所有数据源
        return DataSource.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'files']:
            # 对于读取操作，所有认证用户都有权限
            return [permissions.IsAuthenticated()]
        # 对于修改操作，需要管理员权限
        return [permissions.IsAuthenticated(), IsAdminOrReadOnly()]

    def perform_create(self, serializer):
        try:
            data_source = serializer.save(created_by=self.request.user)
            print(f"🔧 [DataSource] 正在创建数据源: {data_source.name}, ID: {data_source.id}")
            print(f"🔧 [DataSource] 当前用户: {self.request.user.username}")

            # 创建活动记录 - 修复调用
            from activities.utils import create_data_source_activity
            result = create_data_source_activity(
                user=self.request.user,
                data_source_name=data_source.name,
                data_source_id=data_source.id,
                action='created'
            )

            if result:
                print(f"✅ [DataSource] 成功创建数据源活动记录: {result.description}")
            else:
                print(f"❌ [DataSource] 创建数据源活动记录失败")

        except Exception as e:
            print(f"❌ [DataSource] 创建数据源时发生错误: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")

    def perform_destroy(self, instance):
        print(f"🔧 [DataSource] 正在删除数据源: {instance.name}, ID: {instance.id}")

        # 创建删除活动记录
        create_data_source_activity(
            user=self.request.user,
            data_source_name=instance.name,
            data_source_id=instance.id,
            action='deleted'
        )

        print(f"✅ [DataSource] 数据源删除活动记录已创建")
        super().perform_destroy(instance)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_file(self, request, pk=None):
        """上传文件到数据源"""
        data_source = self.get_object()
        file = request.FILES.get('file')

        if not file:
            return Response({'error': '没有提供文件'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户权限 - 只有创建者或管理员可以上传文件
        if data_source.created_by != request.user and request.user.role != 'admin':
            return Response({'error': '没有权限访问此数据源'}, status=status.HTTP_403_FORBIDDEN)

        try:
            print(f"开始处理文件: {file.name}, 大小: {file.size} bytes")

            file_info = {
                'filename': file.name,
                'size': file.size,
                'content_type': file.content_type,
                'upload_time': timezone.now().isoformat()
            }

            # 根据文件类型处理
            if file.name.lower().endswith('.json'):
                return self._handle_json_file(file, data_source, request.user, file_info)
            elif file.name.lower().endswith('.csv'):
                return self._handle_csv_file(file, data_source, request.user, file_info)
            elif file.name.lower().endswith(('.xlsx', '.xls')):
                return self._handle_excel_file(file, data_source, request.user, file_info)
            else:
                return Response({'error': '不支持的文件格式，仅支持 CSV、Excel、JSON'},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"文件处理异常: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return Response({'error': f'文件处理失败: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_json_file(self, file, data_source, user, file_info):
        """处理JSON文件 - 修复版本"""
        try:
            # 重置文件指针
            file.seek(0)

            # 读取文件内容
            file_content = file.read().decode('utf-8')

            if not file_content.strip():
                return Response({'error': 'JSON文件为空'}, status=status.HTTP_400_BAD_REQUEST)

            # 解析JSON
            json_data = json.loads(file_content)
            print(f"原始JSON数据类型: {type(json_data)}")

            # 统一处理为记录列表
            records_to_save = []

            if isinstance(json_data, list):
                # 如果是数组格式，直接使用
                records_to_save = json_data
                print(f"数组格式，记录数: {len(records_to_save)}")

            elif isinstance(json_data, dict):
                # 如果是对象格式，查找常见的数据字段
                data_fields = ['RECORDS', 'records', 'data', 'items', 'results']
                found_data = False

                for field in data_fields:
                    if field in json_data and isinstance(json_data[field], list):
                        records_to_save = json_data[field]
                        print(f"找到数据字段 '{field}'，记录数: {len(records_to_save)}")
                        found_data = True
                        break

                if not found_data:
                    # 如果没有找到数据字段，将整个对象作为单条记录
                    records_to_save = [json_data]
                    print("对象格式，作为单条记录处理")
            else:
                return Response({'error': '不支持的JSON格式'}, status=status.HTTP_400_BAD_REQUEST)

            if not records_to_save:
                return Response({'error': 'JSON数据为空'}, status=status.HTTP_400_BAD_REQUEST)

            # 清理数据，确保JSON可序列化
            cleaned_records = []
            for record in records_to_save:
                try:
                    cleaned_record = self._clean_json_data(record)
                    cleaned_records.append(cleaned_record)
                except Exception as e:
                    print(f"清理记录时出错，跳过: {str(e)}")
                    continue

            if not cleaned_records:
                return Response({'error': '所有数据记录都无法处理'}, status=status.HTTP_400_BAD_REQUEST)

            # 创建数据集
            dataset_name = f"{data_source.name} - {file.name}"
            dataset = Dataset.objects.create(
                name=dataset_name,
                data_source=data_source,
                data_type='json',
                description=f'从文件 {file.name} 导入的JSON数据，大小: {file.size} 字节',
                data_structure={'fields': list(cleaned_records[0].keys())} if cleaned_records else {},
                created_by=user
            )

            # 批量创建数据记录
            records_created = 0
            batch_size = 50

            for i in range(0, len(cleaned_records), batch_size):
                batch = cleaned_records[i:i + batch_size]
                data_records = [
                    DataRecord(dataset=dataset, data=record)
                    for record in batch
                ]
                DataRecord.objects.bulk_create(data_records)
                records_created += len(batch)

            # 创建数据集活动记录
            create_dataset_activity(
                user=user,
                dataset_name=dataset.name,
                dataset_id=dataset.id,
                action='created'
            )

            file_info['records_created'] = records_created
            file_info['dataset_id'] = dataset.id
            file_info['total_records'] = len(cleaned_records)

            return Response({
                'message': 'JSON文件上传成功',
                'file_info': file_info,
                'data_source_id': data_source.id,
                'records_created': records_created,
                'total_records': len(cleaned_records),
                'dataset_id': dataset.id
            })

        except json.JSONDecodeError as e:
            return Response({'error': f'JSON文件解析失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"处理JSON文件时出错: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return Response({'error': f'处理JSON文件时出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_csv_file(self, file, data_source, user, file_info):
        """处理CSV文件 - 修复版本"""
        try:
            # 重置文件指针
            file.seek(0)

            # 使用pandas读取CSV文件，处理各种编码
            file_content = file.read()

            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            df = None

            for encoding in encodings:
                try:
                    file_content_decoded = file_content.decode(encoding)
                    df = pd.read_csv(StringIO(file_content_decoded))
                    print(f"成功使用 {encoding} 编码读取CSV文件")
                    break
                except (UnicodeDecodeError, Exception) as e:
                    print(f"编码 {encoding} 失败: {str(e)}")
                    continue

            if df is None:
                return Response({'error': '无法解析CSV文件，请检查文件编码'},
                                status=status.HTTP_400_BAD_REQUEST)

            return self._handle_dataframe(df, file, data_source, user, file_info, 'csv')

        except Exception as e:
            print(f"处理CSV文件时出错: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return Response({'error': f'处理CSV文件时出错: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_excel_file(self, file, data_source, user, file_info):
        """处理Excel文件"""
        try:
            # 使用pandas读取Excel文件
            df = pd.read_excel(BytesIO(file.read()))

            return self._handle_dataframe(df, file, data_source, user, file_info, 'excel')

        except Exception as e:
            return Response({'error': f'处理Excel文件时出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_dataframe(self, df, file, data_source, user, file_info, data_type):
        """通用DataFrame处理逻辑 - 修复版本"""
        try:
            if df.empty:
                return Response({'error': '文件数据为空'}, status=status.HTTP_400_BAD_REQUEST)

            # 清理数据：处理NaN值和非JSON可序列化类型
            df_cleaned = df.where(pd.notnull(df), None)

            # 确保所有数据都是JSON可序列化的
            for col in df_cleaned.columns:
                # 转换非JSON可序列化的类型
                if df_cleaned[col].dtype == 'object':
                    df_cleaned[col] = df_cleaned[col].apply(
                        lambda x: str(x) if not isinstance(x, (str, int, float, bool, type(None))) else x
                    )

            # 创建数据集
            dataset_name = f"{data_source.name} - {file.name}"
            dataset = Dataset.objects.create(
                name=dataset_name,
                data_source=data_source,
                data_type=data_type,
                description=f'从文件 {file.name} 导入的数据，大小: {file.size} 字节',
                data_structure={'fields': df_cleaned.columns.tolist()},
                created_by=user
            )

            print(f"🔧 [Dataset] 正在创建数据集: {dataset.name}, ID: {dataset.id}")

            # 创建活动记录
            result = create_dataset_activity(
                user=user,
                dataset_name=dataset.name,
                dataset_id=dataset.id,
                action='created'
            )

            if result:
                print(f"✅ [Dataset] 成功创建数据集活动记录")
            else:
                print(f"❌ [Dataset] 创建数据集活动记录失败")

            # 批量创建数据记录 - 使用更小的批次大小
            records_created = 0
            batch_size = 50  # 减小批次大小以避免JSON验证问题

            for i in range(0, len(df_cleaned), batch_size):
                batch_df = df_cleaned.iloc[i:i + batch_size]
                data_records = []

                for _, row in batch_df.iterrows():
                    try:
                        # 确保数据是有效的JSON
                        row_data = row.to_dict()

                        # 进一步清理数据
                        cleaned_data = {}
                        for key, value in row_data.items():
                            if pd.isna(value) or value is None:
                                cleaned_data[key] = None
                            elif isinstance(value, (pd.Timestamp, pd.DatetimeIndex)):
                                cleaned_data[key] = value.isoformat()
                            elif isinstance(value, (int, float, str, bool)):
                                cleaned_data[key] = value
                            else:
                                # 其他类型转换为字符串
                                cleaned_data[key] = str(value)

                        # 验证JSON可序列化
                        import json
                        json.dumps(cleaned_data)  # 如果失败会抛出异常

                        data_records.append(DataRecord(
                            dataset=dataset,
                            data=cleaned_data
                        ))

                    except Exception as e:
                        print(f"处理行数据时出错: {str(e)}")
                        # 跳过有问题的行，继续处理其他行
                        continue

                if data_records:
                    DataRecord.objects.bulk_create(data_records)
                    records_created += len(data_records)

            # 创建数据集活动记录
            create_dataset_activity(
                user=user,
                dataset_name=dataset.name,
                dataset_id=dataset.id,
                action='created'
            )

            file_info['records_created'] = records_created
            file_info['dataset_id'] = dataset.id
            file_info['total_rows'] = len(df_cleaned)

            return Response({
                'message': f'{data_type.upper()}文件上传成功',
                'file_info': file_info,
                'data_source_id': data_source.id,
                'records_created': records_created,
                'total_rows': len(df_cleaned)
            })

        except Exception as e:
            print(f"处理DataFrame时出错: {str(e)}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return Response({'error': f'处理数据时出错: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def import_table(self, request, pk=None):
        """导入表数据"""
        data_source = self.get_object()
        table_name = request.data.get('table_name')
        dataset_name = request.data.get('dataset_name', f'{data_source.name} - {table_name}')

        print(f"开始导入表: {table_name}")
        print(f"数据源: {data_source.id} - {data_source.name}")
        print(f"数据集名称: {dataset_name}")
        print(f"连接配置: {data_source.connection_config}")

        if not table_name:
            return Response({'error': '缺少表名'}, status=status.HTTP_400_BAD_REQUEST)

        if data_source.type != 'database':
            return Response({'error': '此数据源不是数据库类型'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户权限 - 只有创建者或管理员可以导入表
        if data_source.created_by != request.user and request.user.role != 'admin':
            return Response({'error': '没有权限访问此数据源'}, status=status.HTTP_403_FORBIDDEN)

        try:
            success, message, dataset_id = DatabaseConnector.import_table_data(
                data_source.connection_config,
                table_name,
                dataset_name,
                request.user,
                data_source
            )

            print(f"导入结果: success={success}, message={message}, dataset_id={dataset_id}")

            if success:
                # 创建数据集活动记录
                create_dataset_activity(
                    user=request.user,
                    dataset_name=dataset_name,
                    dataset_id=dataset_id,
                    action='created'
                )

                return Response({
                    'success': True,
                    'message': message,
                    'dataset_id': dataset_id
                })
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"导入表数据错误详情: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return Response({'error': f'导入表数据时出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        """获取数据源关联的文件列表"""
        data_source = self.get_object()

        # 所有认证用户都可以查看文件列表，不需要权限检查
        try:
            # 获取该数据源下的所有数据集
            datasets = Dataset.objects.filter(data_source=data_source)

            file_list = []
            for dataset in datasets:
                records_count = DataRecord.objects.filter(dataset=dataset).count()

                # 从描述中提取原始文件大小
                original_size = 0
                if '原始大小' in dataset.description:
                    import re
                    size_match = re.search(r'原始大小:\s*(\d+)\s*字节', dataset.description)
                    if size_match:
                        original_size = int(size_match.group(1))

                # 优先使用原始大小，如果没有则估算
                file_size = original_size if original_size > 0 else records_count * 200 + 2000

                file_info = {
                    'id': dataset.id,
                    'filename': f"{dataset.name}.{dataset.data_type}",
                    'dataset_name': dataset.name,
                    'data_type': dataset.data_type,
                    'size': file_size,  # 使用实际或估算的大小
                    'records_count': records_count,
                    'upload_time': dataset.created_at.isoformat(),
                    'description': dataset.description
                }
                file_list.append(file_info)

            return Response({
                'data_source_id': data_source.id,
                'data_source_name': data_source.name,
                'files': file_list,
                'total_files': len(file_list)
            })

        except Exception as e:
            return Response({'error': f'获取文件列表失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # 所有认证用户都可以看到所有数据集
        return Dataset.objects.all()

    # 确保查看用户有读取权限
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'preview', 'data']:
            # 对于读取操作，所有认证用户都有权限
            return [permissions.IsAuthenticated()]
        # 对于修改操作，保持原有权限控制
        return [permissions.IsAuthenticated(), IsAdminOrAnalyst()]

    def perform_create(self, serializer):
        print("🔧 [DEBUG] DatasetViewSet.perform_create 被调用")
        try:
            dataset = serializer.save(created_by=self.request.user)
            print(f"🔧 [DEBUG] 数据集创建成功: {dataset.name}, ID: {dataset.id}")

            # 创建活动记录 - 修复调用
            from activities.utils import create_dataset_activity
            result = create_dataset_activity(
                user=self.request.user,
                dataset_name=dataset.name,
                dataset_id=dataset.id,
                action='created'
            )

            if result:
                print(f"✅ [DEBUG] 数据集活动记录创建成功: {result.description}")
            else:
                print(f"❌ [DEBUG] 数据集活动记录创建失败")

        except Exception as e:
            print(f"❌ [DEBUG] 创建数据集时发生错误: {str(e)}")

    def perform_destroy(self, instance):
        print(f"🔧 [Dataset] 正在删除数据集: {instance.name}, ID: {instance.id}")

        # 创建删除活动记录
        create_dataset_activity(
            user=self.request.user,
            dataset_name=instance.name,
            dataset_id=instance.id,
            action='deleted'
        )

        print(f"✅ [Dataset] 数据集删除活动记录已创建")
        super().perform_destroy(instance)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """获取数据集的数据记录"""
        dataset = self.get_object()
        records = DataRecord.objects.filter(dataset=dataset)

        # 返回数据记录
        data = {
            'dataset_id': dataset.id,
            'dataset_name': dataset.name,
            'records': [
                {
                    'id': record.id,
                    'data': record.data,
                    'created_at': record.created_at
                } for record in records
            ],
            'total_count': records.count()
        }

        return Response(data)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """获取数据集预览数据（所有认证用户都可以访问）"""
        try:
            dataset = self.get_object()
            limit = int(request.query_params.get('limit', 100))

            # 获取限制数量的记录
            records = DataRecord.objects.filter(dataset=dataset)[:limit]

            # 处理数据格式
            all_data = []
            columns_set = set()

            for record in records:
                record_data = record.data
                if isinstance(record_data, dict) and 'RECORDS' in record_data:
                    if isinstance(record_data['RECORDS'], list):
                        all_data.extend(record_data['RECORDS'])
                    else:
                        all_data.append(record_data['RECORDS'])
                else:
                    all_data.append(record_data)

                # 收集所有列名
                if all_data:
                    columns_set.update(all_data[-1].keys())

            # 转换为列表并排序
            columns = sorted(list(columns_set))

            return Response({
                'dataset_id': dataset.id,
                'dataset_name': dataset.name,
                'columns': columns,
                'data': all_data,
                'total_records': DataRecord.objects.filter(dataset=dataset).count(),
                'preview_count': len(all_data),
                'limit': limit
            })

        except Exception as e:
            print(f"预览错误: {str(e)}")
            return Response({'error': f'获取预览数据失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """导出数据集数据"""
        try:
            dataset = self.get_object()

            # 检查用户权限
            if dataset.created_by != request.user:
                return Response({'error': '没有权限访问此数据集'}, status=status.HTTP_403_FORBIDDEN)

            # 获取查询参数
            export_format = request.query_params.get('format', 'csv')
            limit = request.query_params.get('limit')
            page = request.query_params.get('page')
            page_size = request.query_params.get('page_size')

            # 构建查询
            records_query = DataRecord.objects.filter(dataset=dataset)

            # 应用分页
            if page and page_size:
                paginator = StandardPagination()
                page_size = int(page_size)
                page = int(page)
                start = (page - 1) * page_size
                end = start + page_size
                records = records_query[start:end]
            elif limit:
                records = records_query[:int(limit)]
            else:
                records = records_query[:1000]  # 默认最多1000条

            # 处理数据
            all_data = []
            for record in records:
                record_data = record.data
                if isinstance(record_data, dict) and 'RECORDS' in record_data:
                    if isinstance(record_data['RECORDS'], list):
                        all_data.extend(record_data['RECORDS'])
                    else:
                        all_data.append(record_data['RECORDS'])
                else:
                    all_data.append(record_data)

            # 根据格式返回数据
            if export_format == 'csv':
                return self._export_to_csv(all_data, dataset.name)
            else:
                return Response({
                    'data': all_data,
                    'total': len(all_data),
                    'dataset_name': dataset.name
                })

        except Exception as e:
            return Response({'error': f'导出数据失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _export_to_csv(self, data, dataset_name):
        """导出为CSV格式"""
        import csv
        from django.http import HttpResponse

        if not data:
            return HttpResponse('No data to export', status=400)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{dataset_name}.csv"'

        # 获取所有列名
        columns = set()
        for item in data:
            columns.update(item.keys())
        columns = sorted(list(columns))

        writer = csv.DictWriter(response, fieldnames=columns)
        writer.writeheader()

        for item in data:
            # 确保每行都有所有列
            row = {col: item.get(col, '') for col in columns}
            writer.writerow(row)

        return response


class DataRecordViewSet(viewsets.ModelViewSet):
    queryset = DataRecord.objects.all()
    serializer_class = DataRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # 所有认证用户都可以看到所有数据记录
        return DataRecord.objects.all()

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """批量创建数据记录"""
        records_data = request.data.get('records', [])
        dataset_id = request.data.get('dataset')

        if not dataset_id or not records_data:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dataset = Dataset.objects.get(id=dataset_id, created_by=request.user)
            records_to_create = [
                DataRecord(dataset=dataset, data=record_data)
                for record_data in records_data
            ]

            # 使用批量创建，设置合适的批次大小
            batch_size = 100
            created_count = 0
            for i in range(0, len(records_to_create), batch_size):
                batch = records_to_create[i:i + batch_size]
                DataRecord.objects.bulk_create(batch)
                created_count += len(batch)

            return Response({
                'message': f'成功创建 {created_count} 条记录',
                'created_count': created_count
            })

        except Dataset.DoesNotExist:
            return Response({'error': '数据集不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'创建记录失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
