# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/datasets/serializers.py
from rest_framework import serializers
from .models import DataSource, Dataset, DataRecord


class DataSourceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DataSource
        fields = '__all__'

class DatasetSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    record_count = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'data_source', 'data_source_name',
            'data_type',  # 确保包含这个字段
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'record_count'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_record_count(self, obj):
        return obj.datarecord_set.count()

class DataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataRecord
        fields = '__all__'