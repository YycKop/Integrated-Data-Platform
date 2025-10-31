// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/stores/auth.js
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
      user.value = null
      isAuthenticated.value = false
      throw error
    }
  }

  const testConnection = async () => {
    try {
      await authAPI.getCsrfToken()
      return true
    } catch (error) {
      console.error('后端连接测试失败:', error)
      return false
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
