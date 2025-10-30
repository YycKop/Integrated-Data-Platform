# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/dashboards/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class Dashboard(models.Model):
    name = models.CharField(max_length=255, verbose_name='看板名称')
    description = models.TextField(blank=True, verbose_name='描述')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboards',
                             verbose_name='创建者')
    layout_config = models.JSONField(default=dict, verbose_name='布局配置')
    chart_configs = models.JSONField(default=list, verbose_name='图表配置')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'dashboards'
        ordering = ['-created_at']
        verbose_name = '数据看板'
        verbose_name_plural = '数据看板'

    def __str__(self):
        return self.name

    @property
    def charts_count(self):
        return len(self.chart_configs)


class Chart(models.Model):
    CHART_TYPES = (
        ('line', '折线图'),
        ('bar', '柱状图'),
        ('pie', '饼图'),
        ('scatter', '散点图'),
        ('table', '表格'),
        ('map', '地图'),
    )

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='charts')
    name = models.CharField(max_length=255, verbose_name='图表名称')
    chart_type = models.CharField(max_length=50, choices=CHART_TYPES, verbose_name='图表类型')
    dataset_id = models.IntegerField(verbose_name='数据集ID')
    config = models.JSONField(default=dict, verbose_name='图表配置')
    position = models.JSONField(default=dict, verbose_name='位置配置')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'dashboard_charts'
        ordering = ['position']
        verbose_name = '看板图表'
        verbose_name_plural = '看板图表'

    def __str__(self):
        return f"{self.dashboard.name} - {self.name}"