# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/activities/middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class ActivityLoggingMiddleware(MiddlewareMixin):
    """
    活动记录中间件 - 记录所有创建、更新、删除操作
    """

    def process_response(self, request, response):
        # 只处理成功的修改操作
        if response.status_code in [200, 201, 204]:
            self._log_activity(request, response)
        return response

    def _log_activity(self, request, response):
        try:
            # 检查是否是创建操作
            if request.method == 'POST' and response.status_code == 201:
                self._handle_create_activity(request, response)
            # 检查是否是更新操作
            elif request.method in ['PUT', 'PATCH'] and response.status_code == 200:
                self._handle_update_activity(request, response)
            # 检查是否是删除操作
            elif request.method == 'DELETE' and response.status_code == 204:
                self._handle_delete_activity(request, response)

        except Exception as e:
            logger.error(f"活动记录中间件错误: {str(e)}")

    def _handle_create_activity(self, request, response):
        path = request.path
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            return

        print(f"🎯 [Middleware] 检测到创建操作: {path}")
        print(f"🎯 用户: {user.username}")
        print(f"🎯 请求数据: {request.data}")

        # 根据路径判断资源类型
        if '/dashboards/' in path:
            self._create_dashboard_activity(request, response, user)
        elif '/datasets/' in path:
            self._create_dataset_activity(request, response, user)
        elif '/data-sources/' in path:
            self._create_data_source_activity(request, response, user)
        elif '/visualizations/' in path:
            self._create_visualization_activity(request, response, user)

    def _create_dashboard_activity(self, request, response, user):
        try:
            from .utils import create_dashboard_activity

            # 从响应数据获取看板信息
            response_data = response.data
            dashboard_id = response_data.get('id')
            dashboard_name = response_data.get('name')

            if dashboard_id and dashboard_name:
                create_dashboard_activity(
                    user=user,
                    dashboard_name=dashboard_name,
                    dashboard_id=dashboard_id,
                    action='created'
                )
                print(f"✅ 中间件创建看板活动记录成功: {dashboard_name}")

        except Exception as e:
            print(f"❌ 中间件创建看板活动记录失败: {str(e)}")