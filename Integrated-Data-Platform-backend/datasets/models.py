# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/datasets/models.py
from django.db import models
from django.conf import settings  # 添加这行


class DataSource(models.Model):
    SOURCE_TYPES = [
        ('file', '文件上传'),
        ('database', '数据库'),
        ('api', 'API接口'),
    ]

    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '未激活'),
        ('error', '错误'),
    ]

    name = models.CharField(max_length=200, verbose_name="数据源名称")
    type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name="数据源类型")
    description = models.TextField(blank=True, verbose_name="描述")
    connection_config = models.JSONField(default=dict, verbose_name="连接配置")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name="状态")
    last_connection_test = models.DateTimeField(null=True, blank=True, verbose_name="最后连接测试时间")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "数据源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Dataset(models.Model):
    DATA_TYPES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('excel', 'Excel'),
    ]

    name = models.CharField(max_length=200, verbose_name="数据集名称")
    description = models.TextField(blank=True, verbose_name="描述")
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, verbose_name="数据源")
    data_type = models.CharField(max_length=20, choices=DATA_TYPES, verbose_name="数据类型")
    data_structure = models.JSONField(default=dict, verbose_name="数据结构")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="创建者")  # 修改这行
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "数据集"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class DataRecord(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, verbose_name="数据集")
    data = models.JSONField(default=dict, verbose_name="数据记录")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "数据记录"
        verbose_name_plural = verbose_name
