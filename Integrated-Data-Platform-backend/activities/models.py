# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class ActivityType(models.TextChoices):
    DATA_SOURCE_CREATED = 'data_source_created', '创建数据源'
    DATASET_CREATED = 'dataset_created', '创建数据集'
    PIPELINE_EXECUTED = 'pipeline_executed', '执行处理流程'
    VISUALIZATION_CREATED = 'visualization_created', '创建可视化'
    DASHBOARD_CREATED = 'dashboard_created', '创建看板'
    AI_MODEL_TRAINED = 'ai_model_trained', '训练AI模型'
    DATA_PROCESSED = 'data_processed', '数据处理完成'


class Activity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ActivityType.choices)
    description = models.TextField()
    resource_type = models.CharField(max_length=50, blank=True, null=True)
    resource_id = models.IntegerField(blank=True, null=True)
    resource_name = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'activities'
        ordering = ['-created_at']
        verbose_name = '活动记录'
        verbose_name_plural = '活动记录'

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"