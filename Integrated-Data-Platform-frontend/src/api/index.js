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

// 获取CSRF token的函数 - 简化版本
const getCsrfToken = async () => {
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
          // 即使获取失败，也继续请求
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

// 请求拦截器 - 简化版本
api.interceptors.request.use(
  async (config) => {
    // 对于修改数据的请求（POST, PUT, DELETE, PATCH）添加CSRF token
    const method = config.method?.toLowerCase()
    if (['post', 'put', 'delete', 'patch'].includes(method)) {
      try {
        const token = await getCsrfToken()
        if (token) {
          config.headers['X-CSRFToken'] = token
          console.log('🔐 添加CSRF token到请求头')
        }
      } catch (error) {
        console.error('❌ 获取CSRF token失败，但继续请求:', error)
      }
    }

    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 改进错误处理
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
    } else if (error.request) {
      console.error('❌ 网络错误，无法连接到后端服务')
      // 网络错误，可能是后端服务未启动
    }

    return Promise.reject(error)
  }
)

export { api }
