// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/visualization.js
import { api } from './index'

export const visualizationAPI = {
  // 图表类型
  getChartTypes: () => api.get('/chart-types/'),

  // 可视化组件
  getVisualizations: () => api.get('/visualizations/'),
  createVisualization: (data) => api.post('/visualizations/', data),
  updateVisualization: (id, data) => api.put(`/visualizations/${id}/`, data),
  deleteVisualization: (id) => api.delete(`/visualizations/${id}/`),
  getVisualizationData: (id) => api.get(`/visualizations/${id}/data/`),

  // 看板管理
  getDashboards: () => api.get('/dashboards/'),
   createDashboard: async (data) => {
    console.log('🚀 创建看板API调用 - 发送数据:', JSON.stringify(data, null, 2))
    try {
      const response = await api.post('/dashboards/', data)
      console.log('✅ 创建看板API响应:', response)
      return response
    } catch (error) {
      console.error('❌ 创建看板API错误:', error)
      console.error('❌ 错误响应:', error.response?.data)
      throw error
    }
  },

  updateDashboard: async (id, data) => {
    console.log('🚀 更新看板API调用 - 看板ID:', id)
    console.log('🚀 更新看板API调用 - 发送数据:', JSON.stringify(data, null, 2))
    try {
      const response = await api.patch(`/dashboards/${id}/`, data)
      console.log('✅ 更新看板API响应:', response)
      return response
    } catch (error) {
      console.error('❌ 更新看板API错误:', error)
      console.error('❌ 错误响应:', error.response?.data)
      throw error
    }
  },
  deleteDashboard: (id) => api.delete(`/dashboards/${id}/`),
  getDashboardData: (id) => api.get(`/dashboards/${id}/data/`),

  // 数据集字段
  getDatasetColumns: (datasetId) => api.get(`/visualizations/dataset_columns/?dataset_id=${datasetId}`),

  // 新增：看板布局操作
  updateDashboardLayout: (id, layoutData) => api.patch(`/dashboards/${id}/layout/`, layoutData),
  cloneDashboard: (id) => api.post(`/dashboards/${id}/clone/`),
  exportDashboard: (id) => api.get(`/dashboards/${id}/export/`),
}
