import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials)
      user.value = response.user
      isAuthenticated.value = true
      return response
    } catch (error) {
      if (error.response?.status === 400) {
        const errorData = error.response.data
        if (typeof errorData === 'object') {
          // 处理字段级错误
          const errorMessages = Object.values(errorData).flat()
          throw new Error(errorMessages.join(', '))
        }
        throw new Error(errorData?.error || '用户名或密码错误')
      } else {
        throw new Error('登录失败，请检查网络连接')
      }
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      user.value = null
      isAuthenticated.value = false
    }
  }

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      return response
    } catch (error) {
      if (error.response?.status === 400) {
        const errorData = error.response.data
        if (typeof errorData === 'object') {
          // 处理字段级错误
          const errorMessages = Object.values(errorData).flat()
          throw new Error(errorMessages.join(', '))
        }
        throw new Error(errorData?.error || '注册失败，请检查输入信息')
      } else {
        throw new Error('注册失败，请检查网络连接')
      }
    }
  }

  const fetchProfile = async () => {
    try {
      const response = await authAPI.getProfile()
      user.value = response
      isAuthenticated.value = true
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      user.value = null
      isAuthenticated.value = false
      throw error
    }
  }

  const testConnection = async () => {
    try {
      // 首先测试基础连接
      await authAPI.getCsrfToken()
      console.log('✅ 后端连接正常')
      return true
    } catch (error) {
      console.error('❌ 后端连接测试失败:', error)

      // 检查错误类型
      if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        console.error('🔌 网络错误：请确保后端服务已启动')
        throw new Error('无法连接到后端服务，请确保后端服务已启动并运行在 http://localhost:8000')
      } else if (error.response?.status === 404) {
        console.error('🔍 404错误：API端点不存在')
        throw new Error('后端API端点不存在，请检查后端路由配置')
      } else {
        console.error('❌ 其他连接错误:', error.message)
        throw new Error(`连接失败: ${error.message}`)
      }
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    logout,
    register,
    fetchProfile,
    testConnection
  }
})
