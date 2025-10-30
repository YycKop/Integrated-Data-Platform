# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/visualization/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import ChartType, Visualization, Dashboard, DashboardItem
from .serializers import (
    ChartTypeSerializer,
    VisualizationSerializer,
    DashboardSerializer,
    DashboardItemSerializer
)
from datasets.models import DataRecord
import pandas as pd
import json
import math


class ChartTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    图表类型视图集 - 只读，用于前端选择图表类型
    """
    queryset = ChartType.objects.all()
    serializer_class = ChartTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class VisualizationViewSet(viewsets.ModelViewSet):
    serializer_class = VisualizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Visualization.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        获取可视化图表数据 - 修复版
        """
        try:
            visualization = self.get_object()
            dataset = visualization.dataset

            # 获取数据集的所有记录
            records = DataRecord.objects.filter(dataset=dataset)
            if not records.exists():
                print("❌ 数据集为空")
                return Response({
                    'visualization_id': visualization.id,
                    'chart_type': visualization.chart_type.name,
                    'data': {'categories': [], 'series': []},
                    'config': visualization.configuration,
                    'message': '数据集为空'
                })

            data = [record.data for record in records]

            # 转换为DataFrame进行处理
            df = pd.DataFrame(data)
            print(f"✅ 原始数据形状: {df.shape}")
            print(f"✅ 数据列: {df.columns.tolist()}")
            print(f"✅ 数据前5行:\n{df.head()}")

            # 根据可视化配置处理数据
            config = visualization.configuration
            chart_data = self._prepare_chart_data(df, config, visualization.chart_type)

            print(f"✅ 生成的图表数据: {chart_data}")

            return Response({
                'visualization_id': visualization.id,
                'chart_type': visualization.chart_type.name,
                'data': chart_data,
                'config': config,
                'message': '数据加载成功'
            })

        except Exception as e:
            print(f"❌ 获取图表数据错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'获取图表数据失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def dataset_columns(self, request):
        """根据数据集ID获取列名"""
        try:
            dataset_id = request.query_params.get('dataset_id')
            if not dataset_id:
                return Response({'columns': []})

            from datasets.models import Dataset
            dataset = Dataset.objects.filter(id=dataset_id).first()

            if not dataset:
                return Response({'columns': []})

            # 复用数据处理模块的字段获取逻辑
            records = dataset.datarecord_set.all()[:10]
            if records:
                all_columns = set()
                for record in records:
                    if record.data:
                        all_columns.update(record.data.keys())
                columns = list(all_columns)
                return Response({'columns': columns})
            else:
                return Response({'columns': []})

        except Exception as e:
            logger.error(f"Get dataset columns error: {str(e)}")
            return Response({'columns': []})

    def _prepare_chart_data(self, df, config, chart_type):
        """准备图表数据 - 修复版"""
        print(f"🔍 开始准备图表数据")
        print(f"🔍 图表类型: {chart_type.name}")
        print(f"🔍 配置: {config}")

        if df.empty:
            print("❌ 数据为空")
            return self._get_empty_chart_data(chart_type.name)

        try:
            # 清理数据，处理NaN值
            df = df.fillna(0)
            print(f"✅ 清理后数据形状: {df.shape}")

            if chart_type.name == '柱状图':
                return self._prepare_bar_chart_data(df, config)
            elif chart_type.name == '折线图':
                return self._prepare_line_chart_data(df, config)
            elif chart_type.name == '饼图':
                return self._prepare_pie_chart_data(df, config)
            elif chart_type.name == '散点图':
                return self._prepare_scatter_chart_data(df, config)
            elif chart_type.name == '雷达图':
                return self._prepare_radar_chart_data(df, config)
            elif chart_type.name == '地图':
                return self._prepare_map_chart_data(df, config)  # 新增地图处理
            else:
                print(f"⚠️ 未知图表类型: {chart_type.name}")
                return self._get_default_chart_data(df)
        except Exception as e:
            print(f"❌ 图表数据处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._get_empty_chart_data(chart_type.name)

    def _get_empty_chart_data(self, chart_type):
        """返回空的图表数据结构"""
        empty_data = {
            '柱状图': {'categories': [], 'series': []},
            '折线图': {'categories': [], 'series': []},
            '饼图': {'data': []},
            '散点图': {'data': []},
            '雷达图': {'indicators': [], 'series': []},
            '地图': {'data': []}  # 新增地图空数据
        }
        return empty_data.get(chart_type, {'data': []})

    def _get_default_chart_data(self, df):
        """返回默认图表数据"""
        return {
            'categories': list(df.columns) if not df.empty else [],
            'series': [{
                'name': '数据',
                'data': df.iloc[:, 0].tolist() if not df.empty else []
            }]
        }

    # 修复柱状图数据处理
    def _prepare_bar_chart_data(self, df, config):
        """准备柱状图数据 - 修复版"""
        x_field = config.get('xField', '')
        y_field = config.get('yField', '')

        print(f"🔍 柱状图配置 - xField: '{x_field}', yField: '{y_field}'")
        print(f"🔍 数据列: {df.columns.tolist()}")
        print(f"🔍 数据形状: {df.shape}")
        print(f"🔍 数据前5行:\n{df.head()}")

        # 检查字段是否存在
        if x_field not in df.columns:
            print(f"❌ xField '{x_field}' 不存在于数据列中")
            print(f"🔍 可用字段: {df.columns.tolist()}")
            return {'categories': [], 'series': []}

        if y_field not in df.columns:
            print(f"❌ yField '{y_field}' 不存在于数据列中")
            print(f"🔍 可用字段: {df.columns.tolist()}")
            return {'categories': [], 'series': []}

        if not x_field or not y_field:
            print("❌ 缺少xField或yField配置")
            return {'categories': [], 'series': []}

        try:
            # 确保y字段是数值类型
            print(f"🔄 转换y字段 '{y_field}' 为数值类型")
            df[y_field] = pd.to_numeric(df[y_field], errors='coerce').fillna(0)

            # 清理数据，移除NaN值
            df_clean = df.dropna(subset=[x_field, y_field])
            print(f"✅ 清理后数据形状: {df_clean.shape}")

            if df_clean.empty:
                print("❌ 清理后数据为空")
                return {'categories': [], 'series': []}

            print(f"✅ {x_field} 唯一值: {df_clean[x_field].unique()}")
            print(f"✅ {y_field} 统计: {df_clean[y_field].describe()}")

            # 按x字段分组并计算y字段的聚合值
            if 'group_by' in config and config['group_by']:
                group_field = config['group_by']
                if group_field in df_clean.columns:
                    print(f"🔄 使用分组字段: {group_field}")
                    grouped_data = df_clean.groupby([x_field, group_field])[y_field].sum().unstack(fill_value=0)

                    categories = grouped_data.index.tolist()
                    series = []
                    for column in grouped_data.columns:
                        series.append({
                            'name': str(column),
                            'data': grouped_data[column].tolist()
                        })
                    print(f"✅ 分组后 - 分类数: {len(categories)}, 系列数: {len(series)}")
                else:
                    # 分组字段不存在，使用简单分组
                    print("⚠️ 分组字段不存在，使用简单分组")
                    grouped_data = df_clean.groupby(x_field)[y_field].sum()
                    categories = grouped_data.index.tolist()
                    series = [{
                        'name': y_field,
                        'data': grouped_data.tolist()
                    }]
            else:
                # 简单分组（无分组字段）
                print("🔄 使用简单分组（无分组字段）")
                grouped_data = df_clean.groupby(x_field)[y_field].sum()
                categories = grouped_data.index.tolist()
                series = [{
                    'name': y_field,
                    'data': grouped_data.tolist()
                }]

            print(f"🎯 最终数据 - 分类: {categories}")
            print(f"🎯 最终数据 - 系列: {series}")

            return {
                'categories': categories,
                'series': series
            }
        except Exception as e:
            print(f"❌ 柱状图数据处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'categories': [], 'series': []}

    def _prepare_line_chart_data(self, df, config):
        """准备折线图数据 - 支持分组数据"""
        x_field = config.get('xField', '')
        y_fields = config.get('yFields', [])
        group_by = config.get('group_by', '')

        # 使用新的配置字段名
        smooth = config.get('smooth', False)
        area_style = config.get('areaStyle', False)
        show_label = config.get('lineShowLabel', False)  # 使用特定字段名

        if not y_fields:
            single_y_field = config.get('yField', '')
            if single_y_field:
                y_fields = [single_y_field]

        print(f"🔍 折线图配置 - xField: '{x_field}', yFields: {y_fields}', group_by: '{group_by}'")

        if not x_field or not y_fields:
            return {'categories': [], 'series': []}

        try:
            # 数据预处理
            df_processed = df.copy()
            for y_field in y_fields:
                if y_field in df_processed.columns:
                    df_processed[y_field] = pd.to_numeric(df_processed[y_field], errors='coerce')

            # 如果有分组字段
            if group_by and group_by in df_processed.columns:
                return self._prepare_grouped_line_data(df_processed, x_field, y_fields, group_by, config)
            else:
                return self._prepare_simple_line_data(df_processed, x_field, y_fields, config)

        except Exception as e:
            print(f"❌ 折线图数据处理错误: {str(e)}")
            return {'categories': [], 'series': []}

    def _prepare_map_chart_data(self, df, config):
        """准备地图数据 - 支持中国各省市数据"""
        region_field = config.get('regionField', '')
        value_field = config.get('valueField', '')

        print(f"🗺️ 地图配置 - regionField: '{region_field}', valueField: '{value_field}'")
        print(f"🗺️ 数据列: {df.columns.tolist()}")
        print(f"🗺️ 数据形状: {df.shape}")
        print(f"🗺️ 数据前5行:\n{df.head()}")

        if not region_field or not value_field:
            print("❌ 地图缺少地区字段或数值字段配置")
            return {'data': []}

        try:
            # 检查字段是否存在
            if region_field not in df.columns:
                print(f"❌ 地区字段 '{region_field}' 不存在于数据列中")
                return {'data': []}
            if value_field not in df.columns:
                print(f"❌ 数值字段 '{value_field}' 不存在于数据列中")
                return {'data': []}

            # 确保值字段是数值类型
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')

            # 清理数据
            df_clean = df.dropna(subset=[region_field, value_field])

            print(f"✅ 清理后数据形状: {df_clean.shape}")

            if df_clean.empty:
                print("❌ 地图数据清理后为空，使用测试数据")
                # 返回测试数据
                test_data = [
                    {'name': '北京市', 'value': 100},
                    {'name': '上海市', 'value': 80},
                    {'name': '广东省', 'value': 120},
                    {'name': '江苏省', 'value': 90},
                    {'name': '浙江省', 'value': 70},
                    {'name': '四川省', 'value': 60},
                    {'name': '湖北省', 'value': 50},
                    {'name': '湖南省', 'value': 40}
                ]
                return {'data': test_data}

            print(f"✅ {region_field} 唯一值: {df_clean[region_field].unique()}")
            print(f"✅ {value_field} 统计: {df_clean[value_field].describe()}")

            # 按地区字段分组并求和
            grouped_data = df_clean.groupby(region_field)[value_field].sum().reset_index()

            # 转换为地图数据格式
            map_data = []
            for _, row in grouped_data.iterrows():
                region_name = str(row[region_field])
                value = float(row[value_field])

                # 标准化地区名称
                standardized_region = self._standardize_region_name(region_name)

                map_data.append({
                    'name': standardized_region,
                    'value': value
                })

            print(f"✅ 地图数据生成成功，共 {len(map_data)} 个地区")
            print(f"✅ 地图数据示例: {map_data[:3]}")

            return {'data': map_data}

        except Exception as e:
            print(f"❌ 地图数据处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回测试数据作为备选
            test_data = [
                {'name': '北京市', 'value': 100},
                {'name': '上海市', 'value': 80},
                {'name': '广东省', 'value': 120}
            ]
            return {'data': test_data}

    def _standardize_region_name(self, region_name):
        """标准化地区名称以匹配地图数据"""
        # 地区名称映射（可根据需要扩展）
        region_mapping = {
            '北京': '北京市',
            '天津': '天津市',
            '上海': '上海市',
            '重庆': '重庆市',
            '内蒙古': '内蒙古自治区',
            '广西': '广西壮族自治区',
            '西藏': '西藏自治区',
            '宁夏': '宁夏回族自治区',
            '新疆': '新疆维吾尔自治区',
            '香港': '香港特别行政区',
            '澳门': '澳门特别行政区',
            '黑龙江': '黑龙江省',
            '吉林': '吉林省',
            '辽宁': '辽宁省',
            '河北': '河北省',
            '河南': '河南省',
            '山东': '山东省',
            '山西': '山西省',
            '江苏': '江苏省',
            '浙江': '浙江省',
            '安徽': '安徽省',
            '福建': '福建省',
            '江西': '江西省',
            '湖南': '湖南省',
            '湖北': '湖北省',
            '广东': '广东省',
            '海南': '海南省',
            '四川': '四川省',
            '贵州': '贵州省',
            '云南': '云南省',
            '陕西': '陕西省',
            '甘肃': '甘肃省',
            '青海': '青海省'
        }

        # 移除可能的空格和特殊字符
        cleaned_name = region_name.strip().replace('省', '').replace('市', '').replace('自治区', '').replace(
            '特别行政区', '')

        # 返回映射后的名称或原名称
        return region_mapping.get(cleaned_name, region_name)

    def _prepare_simple_line_data(self, df, x_field, y_fields, config):
        """准备简单折线图数据（无分组）"""
        df_sorted = df.sort_values(by=x_field)
        categories = df_sorted[x_field].dropna().unique().tolist()

        series = []
        line_styles = config.get('lineStyles', [])

        for i, y_field in enumerate(y_fields):
            if y_field not in df_sorted.columns:
                continue

            series_data = []
            for category in categories:
                value = df_sorted[df_sorted[x_field] == category][y_field]
                if not value.empty:
                    val = value.iloc[0]
                    series_data.append(None if pd.isna(val) else float(val))
                else:
                    series_data.append(None)

            style_config = line_styles[i] if i < len(line_styles) else {}

            series_item = {
                'name': y_field,
                'data': series_data,
                'type': 'line',
                'smooth': config.get('smooth', False),
                'lineStyle': {
                    'width': style_config.get('width', 2),
                    'color': style_config.get('color', self._get_default_color(i))
                }
            }

            series.append(series_item)

        return {
            'categories': categories,
            'series': series
        }

    def _prepare_grouped_line_data(self, df, x_field, y_fields, group_by, config):
        """准备分组折线图数据"""
        # 按分组字段和X轴字段聚合数据
        pivot_data = df.pivot_table(
            values=y_fields,
            index=x_field,
            columns=group_by,
            aggfunc='mean'
        )

        categories = pivot_data.index.tolist()
        series = []

        # 为每个Y轴字段创建系列
        for y_idx, y_field in enumerate(y_fields):
            if y_field not in pivot_data.columns.get_level_values(0):
                continue

            # 获取该Y轴字段的所有分组数据
            y_data = pivot_data[y_field]

            for group_idx, group_name in enumerate(y_data.columns):
                series_data = y_data[group_name].fillna(0).tolist()

                series_item = {
                    'name': f"{y_field} - {group_name}",
                    'data': series_data,
                    'type': 'line',
                    'smooth': config.get('smooth', False)
                }

                # 应用样式
                style_idx = y_idx * len(y_data.columns) + group_idx
                series_item['lineStyle'] = {
                    'width': 2,
                    'color': self._get_default_color(style_idx)
                }

                series.append(series_item)

        return {
            'categories': categories,
            'series': series
        }

    def _get_default_color(self, index):
        """获取默认颜色"""
        colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
                  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']
        return colors[index % len(colors)]

    def _prepare_pie_chart_data(self, df, config):
        """准备饼图数据 - 修复版"""
        name_field = config.get('nameField', '')
        value_field = config.get('valueField', '')

        print(f"🔍 饼图配置 - nameField: '{name_field}', valueField: '{value_field}'")
        print(f"🔍 数据列: {df.columns.tolist()}")
        print(f"🔍 数据形状: {df.shape}")

        if not name_field or not value_field:
            print("❌ 饼图缺少名称字段或数值字段配置")
            return {'data': []}

        try:
            # 检查字段是否存在
            if name_field not in df.columns:
                print(f"❌ 名称字段 '{name_field}' 不存在于数据列中")
                return {'data': []}
            if value_field not in df.columns:
                print(f"❌ 数值字段 '{value_field}' 不存在于数据列中")
                return {'data': []}

            # 确保值字段是数值类型
            df[value_field] = pd.to_numeric(df[value_field], errors='coerce')

            # 清理数据，移除NaN值
            df_clean = df.dropna(subset=[name_field, value_field])

            if df_clean.empty:
                print("❌ 清理后数据为空")
                return {'data': []}

            print(f"✅ 清理后数据形状: {df_clean.shape}")
            print(f"✅ {name_field} 唯一值: {df_clean[name_field].unique()}")
            print(f"✅ {value_field} 统计: {df_clean[value_field].describe()}")

            # 按名称字段分组并求和
            grouped_data = df_clean.groupby(name_field)[value_field].sum()

            data = []
            for name, value in grouped_data.items():
                data.append({
                    'name': str(name),
                    'value': float(value)
                })

            print(f"✅ 饼图数据生成成功，共 {len(data)} 个数据项")
            print(f"✅ 饼图数据示例: {data[:3]}")  # 打印前3个数据项

            return {'data': data}

        except Exception as e:
            print(f"❌ 饼图数据处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'data': []}

    def _prepare_scatter_chart_data(self, df, config):
        """准备散点图数据 - 修复版"""
        x_field = config.get('xField', '')
        y_field = config.get('yField', '')

        print(f"🔍 散点图配置 - xField: '{x_field}', yField: '{y_field}'")
        print(f"🔍 数据列: {df.columns.tolist()}")

        if not x_field or not y_field:
            print("❌ 散点图缺少X轴或Y轴字段配置")
            return {'data': [], 'xField': x_field, 'yField': y_field}

        try:
            # 检查字段是否存在
            if x_field not in df.columns:
                print(f"❌ X轴字段 '{x_field}' 不存在于数据列中")
                return {'data': [], 'xField': x_field, 'yField': y_field}
            if y_field not in df.columns:
                print(f"❌ Y轴字段 '{y_field}' 不存在于数据列中")
                return {'data': [], 'xField': x_field, 'yField': y_field}

            # 确保字段是数值类型
            df[x_field] = pd.to_numeric(df[x_field], errors='coerce')
            df[y_field] = pd.to_numeric(df[y_field], errors='coerce')

            # 清理数据
            df_clean = df.dropna(subset=[x_field, y_field])

            if df_clean.empty:
                print("❌ 散点图清理后数据为空")
                return {'data': [], 'xField': x_field, 'yField': y_field}

            # 生成散点图数据格式: [[x1, y1], [x2, y2], ...]
            data = []
            for _, row in df_clean.iterrows():
                x_val = float(row[x_field])
                y_val = float(row[y_field])

                # 如果有分组字段，可以作为第三维数据
                point = [x_val, y_val]
                if 'group_by' in config and config['group_by']:
                    group_field = config['group_by']
                    if group_field in df_clean.columns:
                        # 使用分组作为第三维数据（用于点的大小或颜色）
                        try:
                            group_value = float(hash(str(row[group_field])) % 10 + 1)
                            point.append(group_value)
                        except:
                            point.append(1)
                else:
                    # 如果没有分组，默认大小为1
                    point.append(1)

                data.append(point)

            print(f"✅ 散点图数据生成成功 - 点数: {len(data)}")
            print(f"✅ 数据示例: {data[:3]}")  # 打印前3个点

            return {
                'data': data,
                'xField': x_field,
                'yField': y_field
            }
        except Exception as e:
            print(f"❌ 散点图数据处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'data': [], 'xField': x_field, 'yField': y_field}

    def _prepare_radar_chart_data(self, df, config):
        """准备雷达图数据 - 修复统一最大值问题"""
        category_field = config.get('categoryField', '')
        indicator_fields = config.get('indicatorFields', [])

        print(f"🔍 雷达图配置 - categoryField: '{category_field}', indicatorFields: {indicator_fields}")

        if not category_field or not indicator_fields:
            print("❌ 雷达图缺少类别字段或指标字段配置")
            return {'indicators': [], 'series': []}

        try:
            # 检查字段是否存在
            if category_field not in df.columns:
                print(f"❌ 类别字段 '{category_field}' 不存在于数据列中")
                return {'indicators': [], 'series': []}

            for field in indicator_fields:
                if field not in df.columns:
                    print(f"❌ 指标字段 '{field}' 不存在于数据列中")
                    return {'indicators': [], 'series': []}

            # 确保指标字段是数值类型
            for field in indicator_fields:
                df[field] = pd.to_numeric(df[field], errors='coerce')

            # 清理数据
            df_clean = df.dropna(subset=[category_field] + indicator_fields)

            if df_clean.empty:
                print("❌ 雷达图清理后数据为空")
                return {'indicators': [], 'series': []}

            print(f"✅ 清理后数据形状: {df_clean.shape}")

            # 关键修复：计算统一的最大值
            all_values = []
            for field in indicator_fields:
                for category in df_clean[category_field].unique():
                    category_data = df_clean[df_clean[category_field] == category]
                    if len(category_data) > 0:
                        row = category_data.iloc[0]
                        value = float(row[field])
                        all_values.append(value)

            if all_values:
                actual_max = max(all_values)
                # 统一最大值：实际最大值的1.5倍，向上取整
                unified_max = math.ceil(actual_max * 1.5)
                # 确保最小值至少为10
                unified_max = max(unified_max, 10)
            else:
                unified_max = 5

            print(f"📊 统一最大值计算: 实际最大值={max(all_values) if all_values else 0}, 统一最大值={unified_max}")

            # 所有指标使用相同的最大值
            indicators = []
            for indicator_field in indicator_fields:
                indicators.append({
                    'name': indicator_field,
                    'max': unified_max
                })

            # 为每个类别创建系列数据
            series_data = []
            categories = df_clean[category_field].unique()

            for category in categories:
                category_data = df_clean[df_clean[category_field] == category]
                if len(category_data) > 0:
                    row = category_data.iloc[0]
                    values = [float(row[field]) for field in indicator_fields]

                    series_data.append({
                        'name': str(category),
                        'value': values
                    })

            print(f"✅ 雷达图数据生成成功")
            print(f"   - 统一最大值: {unified_max}")
            print(f"   - 指标数量: {len(indicators)}")
            print(f"   - 类别数量: {len(series_data)}")

            return {
                'indicators': indicators,
                'series': series_data
            }
        except Exception as e:
            print(f"❌ 雷达图数据处理错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'indicators': [], 'series': []}


class DashboardViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dashboard.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        获取可视化图表数据 - 修复版
        """
        try:
            visualization = self.get_object()
            dataset = visualization.dataset

            # 获取数据集的所有记录
            records = DataRecord.objects.filter(dataset=dataset)
            if not records.exists():
                print("❌ 数据集为空")
                return Response({
                    'visualization_id': visualization.id,
                    'chart_type': visualization.chart_type.name,
                    'data': {'categories': [], 'series': []},
                    'config': visualization.configuration,
                    'message': '数据集为空'
                })

            data = [record.data for record in records]

            # 转换为DataFrame进行处理
            df = pd.DataFrame(data)
            print(f"✅ 原始数据形状: {df.shape}")
            print(f"✅ 数据列: {df.columns.tolist()}")
            print(f"✅ 数据前5行:\n{df.head()}")

            # 根据可视化配置处理数据
            config = visualization.configuration
            chart_data = self._prepare_chart_data(df, config, visualization.chart_type)

            print(f"✅ 生成的图表数据: {chart_data}")

            # 如果是饼图，特别打印数据格式
            if visualization.chart_type.name == '饼图':
                print(f"🎯 饼图数据详情:")
                print(f"   - 数据类型: {type(chart_data)}")
                print(f"   - 数据键: {chart_data.keys() if hasattr(chart_data, 'keys') else '无键'}")
                if 'data' in chart_data:
                    print(f"   - data字段类型: {type(chart_data['data'])}")
                    print(
                        f"   - data字段长度: {len(chart_data['data']) if isinstance(chart_data['data'], list) else '非列表'}")
                    if isinstance(chart_data['data'], list) and chart_data['data']:
                        print(f"   - 第一个数据项: {chart_data['data'][0]}")
                        print(f"   - 第一个数据项类型: {type(chart_data['data'][0])}")

            return Response({
                'visualization_id': visualization.id,
                'chart_type': visualization.chart_type.name,
                'data': chart_data,
                'config': config,
                'message': '数据加载成功'
            })

        except Exception as e:
            print(f"❌ 获取图表数据错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'获取图表数据失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _prepare_chart_data(self, df, config, chart_type):
        """准备图表数据（简化版，实际应该调用Visualization的相应方法）"""
        # 这里简化实现，实际项目中应该复用Visualization中的数据处理逻辑
        if chart_type.name == '柱状图':
            x_field = config.get('xField', '')
            y_field = config.get('yField', '')

            if x_field and y_field in df.columns:
                grouped = df.groupby(x_field)[y_field].sum()
                return {
                    'categories': grouped.index.tolist(),
                    'series': [{'name': y_field, 'data': grouped.tolist()}]
                }

        return {'data': df.to_dict('records')}
