from rest_framework import permissions


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