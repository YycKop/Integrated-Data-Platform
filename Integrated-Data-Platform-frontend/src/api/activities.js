// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/activities.js
import { api } from './index'

export const activitiesAPI = {
  // 获取最近活动 - 简化版本
  getRecentActivities(params = {}) {
    console.log("📡 [activitiesAPI] 调用 getRecentActivities", params)
    return api.get('/activities/recent/', { params })
  },

  // 创建活动记录
  createActivity(data) {
    console.log("📡 [activitiesAPI] 调用 createActivity")
    return api.post('/activities/', data)
  }
}
