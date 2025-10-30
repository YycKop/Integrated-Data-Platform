// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/dashboards.js
import request from './request'  // 修正导入路径

export const dashboardsAPI = {
  // 获取数据看板列表
  getDashboards(params) {
    return request.get('/dashboards', { params })
  },

  // 获取单个看板详情
  getDashboard(id) {
    return request.get(`/dashboards/${id}`)
  },

  // 创建看板
  createDashboard(data) {
    return request.post('/dashboards', data)
  },

  // 更新看板
  updateDashboard(id, data) {
    return request.put(`/dashboards/${id}`, data)
  },

  // 删除看板
  deleteDashboard(id) {
    return request.delete(`/dashboards/${id}`)
  }
}
