// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/processing.js
import { api } from './index'

export const processingAPI = {
  getPipelines: () => api.get('/processing-pipelines/'),
  createPipeline: (data) => api.post('/processing-pipelines/', data),
  updatePipeline: (id, data) => api.put(`/processing-pipelines/${id}/`, data),
  deletePipeline: (id) => api.delete(`/processing-pipelines/${id}/`),
  executePipeline: (id) => api.post(`/processing-pipelines/${id}/execute/`),
  getDatasetColumns: (id) => api.get(`/processing-pipelines/${id}/dataset_columns/`),
  getDatasetColumnsById: (datasetId) => api.get(`/processing-pipelines/dataset_columns_by_id/?dataset_id=${datasetId}`),

  // 新增：获取处理任务列表
  getProcessings: (params) => api.get('/processing-tasks/', { params }),

  // 或者使用 pipelines 作为处理任务数据
  getProcessingTasks: () => api.get('/processing-pipelines/')
}
