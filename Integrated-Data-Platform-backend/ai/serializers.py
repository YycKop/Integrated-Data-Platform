# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/ai/serializers.py
from rest_framework import serializers
from .models import AIModel, PredictionTask


class AIModelSerializer(serializers.ModelSerializer):
    """
    AI模型序列化器
    用于AI模型的序列化和反序列化，包含显示字段和关联字段
    """

    # 只读显示字段 - 将choice字段的值转换为可读的显示文本
    model_type_display = serializers.CharField(
        source='get_model_type_display',
        read_only=True,
        help_text="模型类型显示名称"
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
        help_text="状态显示名称",
    )

    # 关联字段显示 - 显示关联对象的相关信息而不是ID
    training_data_name = serializers.CharField(
        source='training_data.name',
        read_only=True,
        help_text="训练数据集名称"
    )
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True,
        help_text="创建者用户名"
    )

    class Meta:
        model = AIModel
        fields = [
            # 基础信息字段
            'id', 'name', 'model_type', 'model_type_display', 'description',
            'version', 'status', 'status_display', 'accuracy', 'model_file',

            # 模型配置字段
            'feature_columns', 'target_column', 'training_config',

            # 关联字段
            'training_data', 'training_data_name', 'created_by', 'created_by_name',

            # 时间戳字段
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_by',  # 创建者自动设置为当前用户
            'created_at',  # 创建时间自动设置
            'updated_at'  # 更新时间自动设置
        ]

    def validate_name(self, value):
        """
        验证模型名称
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError("模型名称至少需要2个字符")
        return value

    def validate_accuracy(self, value):
        """
        验证准确率范围
        """
        if value is not None and (value < 0 or value > 1):
            raise serializers.ValidationError("准确率必须在0到1之间")
        return value

    def create(self, validated_data):
        """
        创建AI模型实例，自动设置创建者
        """
        # 从上下文中获取当前用户并设置为创建者
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PredictionTaskSerializer(serializers.ModelSerializer):
    """
    预测任务序列化器
    用于预测任务的序列化和反序列化
    """

    # 只读显示字段
    task_type_display = serializers.CharField(
        source='get_task_type_display',
        read_only=True,
        help_text="任务类型显示名称"
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
        help_text="状态显示名称"
    )

    # 关联字段显示
    ai_model_name = serializers.CharField(
        source='ai_model.name',
        read_only=True,
        help_text="AI模型名称"
    )
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True,
        help_text="创建者用户名"
    )

    class Meta:
        model = PredictionTask
        fields = [
            # 基础信息字段
            'id', 'name', 'task_type', 'task_type_display',
            'ai_model', 'ai_model_name', 'input_dataset',

            # 输入输出字段
            'input_parameters', 'output_result', 'output_file',

            # 状态字段
            'status', 'status_display', 'progress', 'error_message',

            # 关联和审计字段
            'created_by', 'created_by_name',

            # 时间字段
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'created_by',  # 创建者自动设置
            'created_at',  # 创建时间自动设置
            'started_at',  # 开始时间由系统设置
            'completed_at'  # 完成时间由系统设置
        ]

    def validate_progress(self, value):
        """
        验证进度值范围
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError("进度必须在0到100之间")
        return value

    def validate_input_parameters(self, value):
        """
        验证输入参数
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("输入参数必须是JSON对象")
        return value

    def create(self, validated_data):
        """
        创建预测任务实例，自动设置创建者
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TrainingRequestSerializer(serializers.Serializer):
    """
    训练请求序列化器
    用于接收模型训练请求的参数验证
    注意：这不是ModelSerializer，因为不直接对应数据库模型
    """

    dataset_id = serializers.IntegerField(
        required=True,
        help_text="训练数据集ID",
        min_value=1  # 确保ID是正整数
    )

    features = serializers.ListField(
        child=serializers.CharField(),  # 列表中的每个元素都是字符串
        required=True,
        help_text="特征列名列表",
        min_length=1  # 至少需要一个特征
    )

    target = serializers.CharField(
        required=True,
        help_text="目标列名",
        min_length=1  # 目标列名不能为空
    )

    config = serializers.DictField(
        default=dict,  # 默认为空字典
        help_text="训练配置参数"
    )

    def validate_features(self, value):
        """
        验证特征列表
        """
        if len(value) != len(set(value)):
            raise serializers.ValidationError("特征列表中存在重复项")
        return value

    def validate(self, data):
        """
        跨字段验证
        """
        # 确保目标列不在特征列表中
        if data['target'] in data['features']:
            raise serializers.ValidationError({
                "target": "目标列不能在特征列表中"
            })
        return data


class PredictionRequestSerializer(serializers.Serializer):
    """
    预测请求序列化器
    用于接收预测请求的参数验证
    """

    input_data = serializers.ListField(
        child=serializers.DictField(),  # 列表中的每个元素都是字典
        required=True,
        help_text="输入数据列表，每个元素为特征字典",
        min_length=1  # 至少需要一条数据
    )

    parameters = serializers.DictField(
        default=dict,
        help_text="预测参数配置"
    )

    def validate_input_data(self, value):
        """
        验证输入数据
        """
        if not value:
            raise serializers.ValidationError("输入数据不能为空列表")

        # 检查所有数据条目的键是否一致
        first_keys = set(value[0].keys()) if value else set()
        for i, item in enumerate(value[1:], start=1):
            if set(item.keys()) != first_keys:
                raise serializers.ValidationError(
                    f"第{i + 1}条数据的特征与第一条不一致"
                )

        return value