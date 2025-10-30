# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/datasets/admin.py
from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(DataSource)
admin.site.register(Dataset)
admin.site.register(DataRecord)
