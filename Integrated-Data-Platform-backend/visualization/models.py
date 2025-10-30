# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/visualization/models.py
from django.db import models
from django.conf import settings  # 添加这行
from datasets.models import Dataset


class ChartType(models.Model):
    name = models.CharField(max_length=100, verbose_name="图表类型名称")
    chart_library = models.CharField(max_length=50, verbose_name="图表库")
    configuration_template = models.JSONField(default=dict, verbose_name="配置模板")

    class Meta:
        verbose_name = "图表类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


def create_default_chart_types():
    """创建默认的图表类型"""
    chart_types = [
        {'name': '柱状图', 'chart_library': 'echarts', 'configuration_template': {}},
        {'name': '折线图', 'chart_library': 'echarts', 'configuration_template': {}},
        {'name': '饼图', 'chart_library': 'echarts', 'configuration_template': {}},
        {'name': '散点图', 'chart_library': 'echarts', 'configuration_template': {}},
        {'name': '雷达图', 'chart_library': 'echarts', 'configuration_template': {}},
        {'name': '地图', 'chart_library': 'echarts', 'configuration_template': {}},
    ]

    for chart_type_data in chart_types:
        ChartType.objects.get_or_create(
            name=chart_type_data['name'],
            defaults=chart_type_data
        )


class Visualization(models.Model):
    name = models.CharField(max_length=200, verbose_name="可视化名称")
    description = models.TextField(blank=True, verbose_name="描述")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, verbose_name="数据集")
    chart_type = models.ForeignKey(ChartType, on_delete=models.CASCADE, verbose_name="图表类型")
    configuration = models.JSONField(default=dict, verbose_name="可视化配置")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="创建者")  # 修改这行
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "可视化"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Dashboard(models.Model):
    name = models.CharField(max_length=200, verbose_name="看板名称")
    description = models.TextField(blank=True, verbose_name="描述")
    visualizations = models.ManyToManyField(Visualization, through='DashboardItem', verbose_name="可视化组件")
    layout_config = models.JSONField(default=dict, verbose_name="布局配置")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="创建者")  # 修改这行
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "看板"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class DashboardItem(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, verbose_name="看板")
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, verbose_name="可视化")
    position_x = models.IntegerField(verbose_name="X位置")
    position_y = models.IntegerField(verbose_name="Y位置")
    width = models.IntegerField(verbose_name="宽度")
    height = models.IntegerField(verbose_name="高度")

    class Meta:
        verbose_name = "看板项"
        verbose_name_plural = verbose_name
