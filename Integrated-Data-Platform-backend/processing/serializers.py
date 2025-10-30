# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/processing/serializers.py
from rest_framework import serializers
from .models import ProcessingPipeline, PipelineModule
from datasets.models import Dataset


class PipelineModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineModule
        fields = ['id', 'name', 'type', 'order', 'configuration']
        read_only_fields = ('id',)

    def validate_name(self, value):
        """如果名称为空，提供默认值"""
        if not value or value.strip() == '':
            return "处理模块"
        return value

    def validate_configuration(self, value):
        """验证配置字段"""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("配置必须是JSON对象")
        return value


class ProcessingPipelineSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    input_dataset_name = serializers.CharField(source='input_dataset.name', read_only=True)
    output_dataset_name_display = serializers.SerializerMethodField()
    modules = PipelineModuleSerializer(many=True, source='pipelinemodule_set', required=False)
    input_dataset_columns = serializers.SerializerMethodField()

    class Meta:
        model = ProcessingPipeline
        fields = [
            'id', 'name', 'description', 'input_dataset', 'output_dataset',
            'output_dataset_name', 'output_data_type', 'created_by', 'created_at',
            'input_dataset_name', 'output_dataset_name_display', 'modules', 'input_dataset_columns'
        ]
        read_only_fields = ('id', 'created_by', 'created_at')

    def get_output_dataset_name_display(self, obj):
        if obj.output_dataset:
            return obj.output_dataset.name
        return obj.output_dataset_name or "新建数据集"

    def get_input_dataset_columns(self, obj):
        """获取输入数据集的列名"""
        if obj.input_dataset:
            try:
                first_record = obj.input_dataset.datarecord_set.first()
                if first_record:
                    return list(first_record.data.keys())
            except Exception:
                pass
        return []

    def validate(self, attrs):
        """整体验证"""
        # 验证输出数据集配置
        has_output_name = 'output_dataset_name' in attrs and attrs.get('output_dataset_name')
        has_output_dataset = 'output_dataset' in attrs and attrs.get('output_dataset')

        if not has_output_name and not has_output_dataset:
            raise serializers.ValidationError({
                'output_dataset': '必须设置输出数据集：创建新数据集或选择现有数据集'
            })

        return attrs

    def create(self, validated_data):
        modules_data = validated_data.pop('pipelinemodule_set', [])

        # 确保输出数据类型有默认值
        if 'output_data_type' not in validated_data:
            validated_data['output_data_type'] = 'json'

        # 创建处理流程
        pipeline = ProcessingPipeline.objects.create(**validated_data)

        # 创建模块
        for i, module_data in enumerate(modules_data):
            module_data['order'] = i + 1
            PipelineModule.objects.create(pipeline=pipeline, **module_data)

        return pipeline

    def update(self, instance, validated_data):
        modules_data = validated_data.pop('pipelinemodule_set', [])

        # 更新管道基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 删除旧的模块并创建新的
        instance.pipelinemodule_set.all().delete()
        for i, module_data in enumerate(modules_data):
            module_data['order'] = i + 1
            PipelineModule.objects.create(pipeline=instance, **module_data)

        return instance

    def to_internal_value(self, data):
        """处理前端传入的数据"""
        # 先调用父类方法处理基本数据
        result = super().to_internal_value(data)

        # 单独处理模块数据
        modules_data = data.get('modules')
        if modules_data is not None:
            # 验证模块数据
            modules_serializer = PipelineModuleSerializer(data=modules_data, many=True)
            if modules_serializer.is_valid():
                result['pipelinemodule_set'] = modules_serializer.validated_data
            else:
                # 如果模块数据验证失败，抛出错误
                raise serializers.ValidationError({
                    'modules': modules_serializer.errors
                })

        return result