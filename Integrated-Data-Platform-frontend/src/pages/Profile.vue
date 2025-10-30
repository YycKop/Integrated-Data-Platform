<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/pages/Profile.vue -->
<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人信息</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>基本信息</span>
          </template>
          <div class="user-info-detail">
            <div class="info-item">
              <span class="label">用户名：</span>
              <span class="value">{{ authStore.user?.username }}</span>
            </div>
            <div class="info-item">
              <span class="label">角色：</span>
              <el-tag :type="getRoleTag(authStore.user?.role)">
                {{ getRoleText(authStore.user?.role) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">邮箱：</span>
              <span class="value">{{ authStore.user?.email || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="label">部门：</span>
              <span class="value">{{ authStore.user?.department || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="label">注册时间：</span>
              <span class="value">{{ formatDate(authStore.user?.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">最后登录：</span>
              <span class="value">{{ formatDate(authStore.user?.last_login) || '未知' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>系统状态</span>
          </template>
          <div class="system-status">
            <div class="status-item">
              <el-icon class="status-icon success"><SuccessFilled /></el-icon>
              <span>后端服务</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
            <div class="status-item">
              <el-icon class="status-icon success"><SuccessFilled /></el-icon>
              <span>数据库</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
            <div class="status-item">
              <el-icon class="status-icon warning"><WarningFilled /></el-icon>
              <span>存储空间</span>
              <el-tag type="warning" size="small">85%</el-tag>
            </div>
            <div class="status-item">
              <el-icon class="status-icon success"><SuccessFilled /></el-icon>
              <span>AI服务</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { SuccessFilled, WarningFilled } from '@element-plus/icons-vue'

const authStore = useAuthStore()

const getRoleTag = (role) => {
  const roleMap = {
    admin: 'danger',
    analyst: 'warning',
    viewer: 'success'
  }
  return roleMap[role] || 'info'
}

const getRoleText = (role) => {
  const roleMap = {
    admin: '管理员',
    analyst: '数据分析师',
    viewer: '查看者'
  }
  return roleMap[role] || role
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.user-info-detail .info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.user-info-detail .info-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.user-info-detail .label {
  color: #606266;
  font-weight: 500;
  min-width: 100px;
}

.user-info-detail .value {
  color: #303133;
  text-align: right;
}

.system-status .status-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 8px 0;
}

.system-status .status-item:last-child {
  margin-bottom: 0;
}

.status-icon {
  margin-right: 12px;
  font-size: 20px;
}

.status-icon.success {
  color: #67c23a;
}

.status-icon.warning {
  color: #e6a23c;
}

.system-status .status-item span {
  flex: 1;
  color: #606266;
}
</style>
