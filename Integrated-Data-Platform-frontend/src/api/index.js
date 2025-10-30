// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/api/index.js
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // 重要：允许携带cookie
  headers: {
    'Content-Type': 'application/json'
  }
})

// 存储CSRF token
let csrfToken = ''
let isGettingCsrfToken = false
let csrfTokenPromise = null

// 从cookie中获取CSRF token的函数
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 获取CSRF token的函数 - 添加防重复请求
const getCsrfToken = async () => {
  // 如果正在获取token，返回同一个promise
  if (isGettingCsrfToken && csrfTokenPromise) {
    return csrfTokenPromise
  }

  isGettingCsrfToken = true

  csrfTokenPromise = new Promise(async (resolve, reject) => {
    try {
      // 首先尝试从cookie获取
      let token = getCookie('csrftoken')
      console.log('🔍 从Cookie获取CSRF token:', token ? '成功' : '失败')

      if (!token) {
        try {
          // 如果cookie中没有，从API获取
          console.log('🔄 从API获取CSRF token...')
          const response = await axios.get('http://localhost:8000/api/auth/csrf/', {
            withCredentials: true
          })
          token = response.data.csrfToken
          console.log('✅ 从API获取CSRF token成功:', token ? '有值' : '空值')
        } catch (error) {
          console.error('❌ 获取CSRF token失败:', error)
          // 即使获取失败，也继续请求，服务器可能会设置cookie
        }
      }

      csrfToken = token || ''
      resolve(csrfToken)
    } catch (error) {
      reject(error)
    } finally {
      isGettingCsrfToken = false
    }
  })

  return csrfTokenPromise
}

// 请求拦截器 - 自动添加CSRF token
api.interceptors.request.use(
  async (config) => {
    // 对于修改数据的请求（POST, PUT, DELETE, PATCH）添加CSRF token
    const method = config.method?.toLowerCase()
    if (['post', 'put', 'delete', 'patch'].includes(method)) {
      try {
        const token = await getCsrfToken()
        if (token) {
          // Django期望的CSRF token头部名称
          config.headers['X-CSRFToken'] = token
          console.log('🔐 添加CSRF token到请求头:', token.substring(0, 10) + '...')
        } else {
          console.warn('⚠️ 没有可用的CSRF token，但继续请求')
        }
      } catch (error) {
        console.error('❌ 获取CSRF token失败，但继续请求:', error)
      }
    }

    // 对于文件上传，确保Content-Type正确
    if (config.data instanceof FormData) {
      // 文件上传时让浏览器自动设置Content-Type和boundary
      delete config.headers['Content-Type']
    }

    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    console.log('Request Headers:', config.headers)

    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response.data
  },
  (error) => {
    console.error('❌ Response Error:', error)

    if (error.response) {
      console.error('Error Status:', error.response.status)
      console.error('Error Data:', error.response.data)

      // 如果是CSRF错误，重新获取token
      if (error.response.status === 403) {
        console.log('🔄 检测到403错误，可能是CSRF token问题，清除token缓存...')
        csrfToken = '' // 清除旧的token
        isGettingCsrfToken = false
        csrfTokenPromise = null
      }
    }

    // 401未授权，跳转到登录页
    if (error.response?.status === 401) {
      console.log('🔐 未授权，跳转到登录页')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export { api }
