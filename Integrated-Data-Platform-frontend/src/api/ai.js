// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/ai.js
import request from './request'

export const aiAPI = {
  // 获取数据集列表
  async getDatasets() {
    try {
      console.log('API: 开始获取数据集列表...')
      const response = await request.get('/api/ai/models/datasets/')
      console.log('API: 数据集原始响应:', response)
      return response
    } catch (error) {
      console.error('API: 获取数据集失败:', error)
      throw error
    }
  },

  // 获取数据集列名
  async getDatasetColumns(datasetId) {
    try {
      console.log(`API: 开始获取数据集 ${datasetId} 的列名...`)
      const response = await request.get('/api/ai/datasets/columns/', {
        params: {dataset_id: datasetId}
      })
      console.log('API: 列名原始响应:', response)
      return response
    } catch (error) {
      console.error('API: 获取列名失败:', error)
      throw error
    }
  },

  // 获取数据集预览
  async getDatasetPreview(datasetId) {
    try {
      console.log(`API: 开始获取数据集 ${datasetId} 的预览...`)
      const response = await request.get('/api/ai/datasets/preview/', {
        params: {dataset_id: datasetId}
      })
      console.log('API: 预览原始响应:', response)
      return response
    } catch (error) {
      console.error('API: 获取预览失败:', error)
      throw error
    }
  },

  // 获取模型列表
  async getModels(params = {}) {
    try {
      console.log('API: 开始获取模型列表...')
      const response = await request.get('/api/ai/models/', {params})
      console.log('API: 模型列表原始响应:', response)
      return response
    } catch (error) {
      console.error('API: 获取模型列表失败:', error)
      throw error
    }
  },

  // 获取单个模型详情 - 新增方法
  async getModel(modelId) {
    try {
      console.log(`API: 开始获取模型详情，ID: ${modelId}`)
      const response = await request.get(`/api/ai/models/${modelId}/`)
      console.log('API: 模型详情原始响应:', response)
      return response
    } catch (error) {
      console.error('API: 获取模型详情失败:', error)
      throw error
    }
  },

  // 创建模型
  async createModel(data) {
    try {
      console.log('API: 开始创建模型...')
      const response = await request.post('/api/ai/models/', data)
      console.log('API: 创建模型响应:', response)
      return response
    } catch (error) {
      console.error('API: 创建模型失败:', error)
      throw error
    }
  },

  // 更新模型
  async updateModel(modelId, data) {
    try {
      console.log(`API: 开始更新模型，ID: ${modelId}`)
      const response = await request.put(`/api/ai/models/${modelId}/`, data)
      console.log('API: 更新模型响应:', response)
      return response
    } catch (error) {
      console.error('API: 更新模型失败:', error)
      throw error
    }
  },
  // 更新模型状态
  async updateModelStatus(modelId, status) {
    try {
      console.log(`API: 更新模型状态，ID: ${modelId}, 状态: ${status}`)
      const response = await request.post(`/api/ai/models/${modelId}/update_status/`, {
        status: status
      })
      console.log('API: 更新状态响应:', response)
      return response
    } catch (error) {
      console.error('API: 更新模型状态失败:', error)
      throw error
    }
  },

  // 开始训练
  async startTraining(modelId, data = {}) {
    try {
      console.log(`API: 开始训练模型，ID: ${modelId}`)
      const response = await request.post(`/api/ai/models/${modelId}/start_training/`, data)
      console.log('API: 开始训练响应:', response)
      return response
    } catch (error) {
      console.error('API: 开始训练失败:', error)
      throw error
    }
  },

  // 完成训练
  async completeTraining(modelId, data = {}) {
    try {
      console.log(`API: 完成模型训练，ID: ${modelId}`)
      const response = await request.post(`/api/ai/models/${modelId}/complete_training/`, data)
      console.log('API: 完成训练响应:', response)
      return response
    } catch (error) {
      console.error('API: 完成训练失败:', error)
      throw error
    }
  },

  // 删除模型
  async deleteModel(modelId) {
    try {
      console.log(`API: 开始删除模型，ID: ${modelId}`)
      const response = await request.delete(`/api/ai/models/${modelId}/`)
      console.log('API: 删除模型响应:', response)
      return response
    } catch (error) {
      console.error('API: 删除模型失败:', error)
      throw error
    }
  },

  // 训练模型
  async trainModel(modelId, data) {
    try {
      console.log(`API: 开始训练模型，ID: ${modelId}`)
      const response = await request.post(`/api/ai/models/${modelId}/train/`, data)
      console.log('API: 训练模型响应:', response)
      return response
    } catch (error) {
      console.error('API: 训练模型失败:', error)
      throw error
    }
  },

  // 模型预测
  async predict(modelId, data) {
    try {
      console.log(`API: 开始模型预测，ID: ${modelId}`)
      const response = await request.post(`/api/ai/models/${modelId}/predict/`, data)
      console.log('API: 预测响应:', response)
      return response
    } catch (error) {
      console.error('API: 预测失败:', error)
      throw error
    }
  },

  // 分析市场趋势
  async analyzeMarketTrends(data) {
    try {
      console.log('API: 开始分析市场趋势...')
      const response = await request.post('/api/ai/analyze-market-trends/', data)
      console.log('API: 市场趋势分析响应:', response)
      return response
    } catch (error) {
      console.error('API: 市场趋势分析失败:', error)
      throw error
    }
  },

  // 生成洞察
  async generateInsights(data) {
    try {
      console.log('API: 开始生成洞察...')
      const response = await request.post('/api/ai/generate-insights/', data)
      console.log('API: 生成洞察响应:', response)
      return response
    } catch (error) {
      console.error('API: 生成洞察失败:', error)
      throw error
    }
  }
}
