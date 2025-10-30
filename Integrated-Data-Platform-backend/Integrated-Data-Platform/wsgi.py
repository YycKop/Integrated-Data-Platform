# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/Integrated-Data-Platform/wsgi.py
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Integrated-Data-Platform.settings")

application = get_wsgi_application()
