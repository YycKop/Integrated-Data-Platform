// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:8000', // 确保这是正确的Django后端地址
  timeout: 10000,
  withCredentials: true
})

// 添加请求拦截器来调试
request.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    console.log('请求数据:', config.data)

    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }

    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 添加详细日志
request.interceptors.response.use(
  (response) => {
    console.log('请求成功:', response.config.url, response.status)
    console.log('响应数据:', response.data)
    return response.data
  },
  (error) => {
    console.error('请求失败:', error.config?.url, error.response?.status)
    console.error('错误详情:', error.response?.data)

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          ElMessage.error(data.message || '请求参数错误')
          break
        case 401:
          ElMessage.error('未授权，请重新登录')
          const authStore = useAuthStore()
          authStore.logout()
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error(`请求的资源不存在: ${error.config.url}`)
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data.message || '网络错误')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接和后端服务')
      console.error('网络错误详情:', error.request)
    } else {
      ElMessage.error('请求配置错误: ' + error.message)
    }

    return Promise.reject(error)
  }
)

// 获取 cookie 的辅助函数
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export default request
