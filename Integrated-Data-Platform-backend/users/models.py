# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

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