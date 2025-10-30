# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/processing/admin.py
from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ProcessingPipeline)
admin.site.register(PipelineModule)