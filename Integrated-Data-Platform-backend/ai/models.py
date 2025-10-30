# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/ai/models.py
from django.db import models
from django.conf import settings


class AIModel(models.Model):
    """
    AI模型信息表
    存储机器学习模型的基本信息、配置和状态
    """

    # 模型类型选择项
    MODEL_TYPES = [
        ('price_prediction', '价格预测'),
        ('yield_prediction', '产量预测'),
        ('disease_detection', '病害检测'),
        ('market_analysis', '市场分析'),
        ('climate_impact', '气候影响分析'),
    ]

    # 模型状态选择项
    STATUS_CHOICES = [
        ('training', '训练中'),
        ('active', '已激活'),
        ('inactive', '未激活'),
        ('error', '错误'),
    ]

    # 基础信息字段
    name = models.CharField(max_length=200, verbose_name='模型名称')
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES, verbose_name='模型类型')
    description = models.TextField(blank=True, verbose_name='模型描述')
    version = models.CharField(max_length=50, default='1.0', verbose_name='版本号')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name='状态')
    accuracy = models.FloatField(null=True, blank=True, verbose_name='准确率')

    # 模型文件相关字段
    model_file = models.FileField(upload_to='ai_models/', null=True, blank=True)  # 上传到media/ai_models/目录
    feature_columns = models.JSONField(default=list, verbose_name='特征列')  # 存储特征列名列表
    target_column = models.CharField(max_length=100, blank=True, verbose_name='目标列')  # 预测目标列名

    # 训练配置字段
    training_config = models.JSONField(default=dict, verbose_name='训练配置')  # 存储超参数等配置
    # 使用字符串引用避免循环导入，SET_NULL保证数据集删除时模型记录不丢失
    training_data = models.ForeignKey(
        'datasets.Dataset',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='训练数据'
    )

    # 审计字段
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'ai_models'  # 自定义数据库表名
        verbose_name = 'AI模型'  # 单数显示名称
        verbose_name_plural = 'AI模型'  # 复数显示名称

    def __str__(self):
        """对象字符串表示"""
        return f"{self.name} ({self.get_model_type_display()})"

    def get_model_info(self):
        """获取模型详细信息（示例方法）"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.get_model_type_display(),
            'status': self.get_status_display(),
            'accuracy': self.accuracy,
            'version': self.version,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class PredictionTask(models.Model):
    """
    预测任务表
    记录AI模型的预测任务执行情况
    """

    # 任务类型选择项
    TASK_TYPES = [
        ('batch_prediction', '批量预测'),  # 对大量数据进行批量预测
        ('realtime_prediction', '实时预测'),  # 单条或少量数据的实时预测
        ('model_training', '模型训练'),  # 模型训练任务
    ]

    # 任务状态选择项
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    # 任务基本信息
    name = models.CharField(max_length=200, verbose_name='任务名称')
    task_type = models.CharField(max_length=50, choices=TASK_TYPES, verbose_name='任务类型')
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, verbose_name='AI模型')  # 关联使用的AI模型
    input_dataset = models.ForeignKey(
        'datasets.Dataset',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='输入数据'
    )  # 预测任务的输入数据集
    input_parameters = models.JSONField(default=dict, verbose_name='输入参数')  # 任务执行参数

    # 输出结果字段
    output_result = models.JSONField(null=True, blank=True, verbose_name='输出结果')  # 存储结构化预测结果
    output_file = models.FileField(upload_to='prediction_results/', null=True, blank=True)  # 结果文件存储

    # 任务执行状态字段
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    progress = models.FloatField(default=0, verbose_name='进度')  # 任务完成进度百分比
    error_message = models.TextField(blank=True, verbose_name='错误信息')  # 任务失败时的错误信息

    # 审计和时间字段
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')  # 任务实际开始时间
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')  # 任务完成时间

    class Meta:
        db_table = 'prediction_tasks'  # 自定义数据库表名
        verbose_name = '预测任务'  # 单数显示名称
        verbose_name_plural = '预测任务'  # 复数显示名称
        ordering = ['-created_at']  # 默认按创建时间降序排列

    def __str__(self):
        """对象字符串表示"""
        return f"{self.name} - {self.get_status_display()}"

    def update_progress(self, progress, commit=True):
        """
        更新任务进度

        Args:
            progress (float): 进度值(0-100)
            commit (bool): 是否立即保存到数据库
        """
        self.progress = progress
        if commit:
            self.save()

    def mark_as_running(self):
        """标记任务为运行中状态"""
        from django.utils import timezone
        self.status = 'running'
        self.started_at = timezone.now()
        self.progress = 0
        self.save()

    def mark_as_completed(self, result=None, output_file=None):
        """标记任务为完成状态"""
        from django.utils import timezone
        self.status = 'completed'
        self.progress = 100
        self.completed_at = timezone.now()
        if result is not None:
            self.output_result = result
        if output_file is not None:
            self.output_file = output_file
        self.save()

    def mark_as_failed(self, error_message):
        """标记任务为失败状态"""
        from django.utils import timezone
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()

    def get_task_duration(self):
        """获取任务执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_completed(self):
        """检查任务是否完成"""
        return self.status == 'completed'

    @property
    def is_failed(self):
        """检查任务是否失败"""
        return self.status == 'failed'

    @property
    def can_be_cancelled(self):
        """检查任务是否可以取消"""
        return self.status in ['pending', 'running']