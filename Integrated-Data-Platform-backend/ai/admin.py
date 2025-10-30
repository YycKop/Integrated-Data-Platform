# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/ai/admin.py
from django.contrib import admin
from .models import AIModel, PredictionTask

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'status', 'accuracy', 'created_at']
    list_filter = ['model_type', 'status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PredictionTask)
class PredictionTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'task_type', 'ai_model', 'status', 'progress', 'created_at']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['name', 'ai_model__name']
    readonly_fields = ['created_at', 'started_at', 'completed_at']