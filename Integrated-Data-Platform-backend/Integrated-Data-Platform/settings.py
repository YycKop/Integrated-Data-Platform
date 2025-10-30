# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/Integrated-Data-Platform/settings.py
import os
from pathlib import Path

# ==================== 基础路径配置 ====================
# 获取项目根目录：__file__是当前文件路径，parent.parent获取到backend目录的父级目录
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== 安全密钥配置 ====================
# Django安全密钥，用于加密签名，生产环境务必使用随机生成的长字符串
SECRET_KEY = 'your-secret-key-here'
# 调试模式，开发时设为True，生产环境必须设为False
DEBUG = True
# 允许访问的主机，开发时使用'*'允许所有，生产环境需指定具体域名
ALLOWED_HOSTS = ['*']

# ==================== 应用配置 ====================
# 已安装的Django应用列表
INSTALLED_APPS = [
    # Django内置核心应用
    'django.contrib.admin',  # 管理员后台
    'django.contrib.auth',  # 认证系统
    'django.contrib.contenttypes',  # 内容类型框架
    'django.contrib.sessions',  # 会话管理
    'django.contrib.messages',  # 消息框架
    'django.contrib.staticfiles',  # 静态文件管理

    # 第三方应用
    'rest_framework',  # Django REST Framework用于构建API
    'corsheaders',  # 处理跨域请求

    # 项目自定义应用
    'users',  # 用户管理应用
    'datasets',  # 数据集管理应用
    'processing',  # 数据处理应用
    'visualization',  # 数据可视化应用
    'ai',  # 人工智能/机器学习应用
    'activities',
    'dashboards',

]

# ==================== 中间件配置 ====================
# 请求/响应处理中间件，按顺序执行
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS跨域中间件，要放在最前面
    'django.middleware.security.SecurityMiddleware',  # 安全相关中间件
    'django.contrib.sessions.middleware.SessionMiddleware',  # 会话管理中间件
    'django.middleware.common.CommonMiddleware',  # 通用中间件
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF保护中间件
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',  # 消息中间件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 点击劫持保护
]

# ==================== URL配置 ====================
# 根URL配置文件的路径
ROOT_URLCONF = 'Integrated-Data-Platform.urls'

# ==================== 模板配置 ====================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # 使用Django模板引擎
        'DIRS': [],  # 额外的模板目录，默认为空
        'APP_DIRS': True,  # 是否在应用内查找模板目录
        'OPTIONS': {
            'context_processors': [  # 模板上下文处理器
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==================== 数据库配置 ====================
# 数据库设置，默认使用SQLite（适合开发）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 数据库引擎
        'NAME': BASE_DIR / 'db.sqlite3',  # 数据库文件路径
    }
}

# ==================== REST Framework配置 ====================
# Django REST Framework设置
REST_FRAMEWORK = {
    # 默认权限类：要求用户认证后才能访问API
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # 默认认证类：使用Session认证
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# ==================== 国际化与本地化配置 ====================
LANGUAGE_CODE = 'zh-hans'  # 中文简体
TIME_ZONE = 'Asia/Shanghai'  # 亚洲/上海时区
USE_I18N = True  # 启用国际化
USE_TZ = True  # 使用时区支持

# ==================== 静态文件配置 ====================
STATIC_URL = '/static/'  # 静态文件URL前缀
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # 静态文件收集目录

# ==================== 模型配置 ====================
# 默认主键字段类型，使用64位自增主键
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# 自定义用户模型
AUTH_USER_MODEL = 'users.UserProfile'

# ==================== Session配置 ====================
# Session SameSite属性：Lax提供基本的CSRF保护，同时允许某些跨站请求
SESSION_COOKIE_SAMESITE = 'Lax'
# Session Cookie只允许HTTP访问，防止JavaScript读取（增强安全性）
SESSION_COOKIE_HTTPONLY = True
# Session Cookie安全传输：开发环境False，生产环境必须设为True（HTTPS）
SESSION_COOKIE_SECURE = False

# ==================== CSRF配置 ====================
# CSRF保护相关设置
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False  # 允许JavaScript读取CSRF token
CSRF_COOKIE_SECURE = False  # 开发环境使用HTTP，生产环境设为True
CSRF_USE_SESSIONS = False  # 使用cookie存储CSRF token（非session）
CSRF_COOKIE_SAMESITE = 'Lax'  # 或 'None' 如果前端在不同域名

# 受信任的CSRF来源（前端应用地址）
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ==================== CORS跨域配置 ====================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# 允许跨域请求携带认证信息（cookies、session等）
CORS_ALLOW_CREDENTIALS = True

# 允许的请求头
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',  # 允许CSRF token头
    'x-requested-with',
]
