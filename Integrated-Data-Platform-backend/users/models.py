# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework import permissions

class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('analyst', '数据分析师'),
        ('viewer', '查看者'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer', verbose_name="角色")
    phone = models.CharField(max_length=20, blank=True, verbose_name="手机号")
    department = models.CharField(max_length=100, blank=True, verbose_name="部门")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # 添加这些字段来覆盖父类，避免冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="userprofile_set",
        related_query_name="userprofile",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="userprofile_set",
        related_query_name="userprofile",
    )

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        db_table = 'users_userprofile'  # 添加这个确保表名唯一

    def __str__(self):
        return self.username

class IsAdmin(permissions.BasePermission):
    """只有管理员有权限"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsViewerOrAbove(permissions.BasePermission):
    """查看者及以上角色有权限（所有认证用户）"""

    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsAnalystOrAbove(permissions.BasePermission):
    """数据分析师及以上角色有权限"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'analyst']


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可以编辑，其他认证用户只能查看"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrAnalyst(permissions.BasePermission):
    """管理员或数据分析师有权限"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'analyst']


class IsOwnerOrAdmin(permissions.BasePermission):
    """对象所有者或管理员有权限"""

    def has_object_permission(self, request, view, obj):
        # 管理员有所有权限
        if request.user.role == 'admin':
            return True

        # 检查对象是否有user字段
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # 检查对象是否有created_by字段
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        # 检查对象是否有owner字段
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class IsCreatorOrAdmin(permissions.BasePermission):
    """创建者或管理员有权限"""

    def has_object_permission(self, request, view, obj):
        # 管理员有所有权限
        if request.user.role == 'admin':
            return True

        # 检查对象是否有created_by字段
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        # 检查对象是否有user字段
        elif hasattr(obj, 'user'):
            return obj.user == request.user

        return False