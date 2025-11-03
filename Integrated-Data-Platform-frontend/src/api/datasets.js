// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/datasets.js
import {api} from './index'

export const datasetsAPI = {
  getDataSources: () => api.get('/data-sources/'),
  createDataSource: (data) => api.post('/data-sources/', data),
  updateDataSource: (id, data) => api.put(`/data-sources/${id}/`, data),
  deleteDataSource: (id) => api.delete(`/data-sources/${id}/`),

  // 数据集API
  getDatasets: (params = {}) => api.get('/datasets/', { params }),
  createDataset: (data) => api.post('/datasets/', data),
  updateDataset: (id, data) => api.put(`/datasets/${id}/`, data),
  deleteDataset: (id) => api.delete(`/datasets/${id}/`),

  getDataset: (id) => api.get(`/datasets/${id}/`),

  // 新增：数据集预览API
  getDatasetPreview: (id, params = {}) => api.get(`/datasets/${id}/preview/`, { params }),

  // 数据记录API（带分页和搜索）
  getDataRecords: (params = {}) => api.get('/data-records/', { params }),
  createDataRecord: (data) => api.post('/data-records/', data),
  bulkCreateDataRecords: (data) => api.post('/data-records/bulk_create/', data),
  deleteDataRecord: (id) => api.delete(`/data-records/${id}/`),

  // 新增：导出API
  exportDatasetData: (id, params = {}) => {
    return api.get(`/datasets/${id}/export/`, {
      params,
      responseType: 'blob' // 重要：用于文件下载
    })
  },

  // 其他API保持不变
  async uploadFile(dataSourceId, formData, config = {}) {
    try {
      const response = await api.post(
        `/data-sources/${dataSourceId}/upload_file/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000,
          ...config
        }
      )
      return response
    } catch (error) {
      console.error('API上传文件错误:', error)
      const errorMsg = error.response?.data?.error ||
                      error.response?.data?.message ||
                      error.message ||
                      '上传失败'
      throw new Error(errorMsg)
    }
  },

  getDataSourceFiles: (dataSourceId) => api.get(`/data-sources/${dataSourceId}/files/`),
  getFilePreview: (datasetId) => api.get(`/datasets/${datasetId}/preview/`),

  // 数据库相关API - 修改这些行
  testConnection: (dataSourceId) => api.post(`/data-sources/${dataSourceId}/test_connection/`),
  getDatabaseTables: (dataSourceId) => api.get(`/data-sources/${dataSourceId}/get_database_tables/`), // 修改这里
  getTablePreview: (dataSourceId, tableName) => api.get(`/data-sources/${dataSourceId}/get_table_preview/?table_name=${tableName}`), // 修改这里
  getTableSchema: (dataSourceId, tableName) => api.get(`/data-sources/${dataSourceId}/table_schema/?table=${tableName}`),
  importTable: (dataSourceId, data) => api.post(`/data-sources/${dataSourceId}/import_table/`, data),
}
