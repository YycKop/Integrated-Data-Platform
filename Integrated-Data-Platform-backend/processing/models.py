# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/processing/models.py
from django.db import models
from django.conf import settings
from datasets.models import Dataset


class ProcessingPipeline(models.Model):
    MODULE_TYPES = [
        ('filter', '数据过滤'),
        ('transform', '数据转换'),
        ('aggregate', '数据聚合'),
        ('clean', '数据清洗'),
        ('select', '数据截取'),
        ('sort', '数据排序'),
    ]

    name = models.CharField(max_length=200, verbose_name="处理流程名称")
    description = models.TextField(blank=True, verbose_name="描述")
    input_dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='input_pipelines',
                                      verbose_name="输入数据集")
    output_dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='output_pipelines',
                                       verbose_name="输出数据集", null=True, blank=True)
    output_dataset_name = models.CharField(max_length=200, verbose_name="输出数据集名称", blank=True)
    # 使用 Dataset 模型中已有的 data_type 字段选项
    output_data_type = models.CharField(max_length=20, choices=Dataset.DATA_TYPES, default='json',
                                       verbose_name="输出数据类型")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "处理流程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PipelineModule(models.Model):
    pipeline = models.ForeignKey(ProcessingPipeline, on_delete=models.CASCADE, verbose_name="处理流程")
    name = models.CharField(max_length=200, verbose_name="模块名称", blank=True, null=True)
    type = models.CharField(max_length=20, choices=ProcessingPipeline.MODULE_TYPES, verbose_name="模块类型")
    order = models.IntegerField(verbose_name="执行顺序")
    configuration = models.JSONField(default=dict, verbose_name="模块配置")

    class Meta:
        verbose_name = "流程模块"
        verbose_name_plural = verbose_name
        ordering = ['order']

    def __str__(self):
        return f"{self.name or '未命名模块'} ({self.get_type_display()})"