# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/Integrated-Data-Platform/asgi.py
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Integrated-Data-Platform.settings")

application = get_asgi_application()
