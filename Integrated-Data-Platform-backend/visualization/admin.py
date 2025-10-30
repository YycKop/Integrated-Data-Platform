# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/visualization/admin.py
from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(ChartType)
admin.site.register(Visualization)
admin.site.register(Dashboard)
