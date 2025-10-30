// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/router/index.js
import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '../stores/auth'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
    meta: {requiresGuest: true}
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../layouts/MainLayout.vue'),
    meta: {requiresAuth: true},
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../pages/Dashboard.vue'),
        meta: { title: '仪表板' }
      },
      {
        path: '/datasets',
        name: 'Datasets',
        component: () => import('../pages/Datasets.vue'),
        meta: { title: '数据集管理' }
      },
      {
        path: '/data-sources',
        name: 'DataSources',
        component: () => import('../pages/DataSources.vue'),
        meta: { title: '数据源管理' }
      },
      {
        path: '/processing',
        name: 'Processing',
        component: () => import('../pages/Processing.vue'),
        meta: { title: '数据处理' }
      },
      {
        path: '/visualization',
        name: 'Visualization',
        component: () => import('../pages/Visualization.vue'),
        meta: { title: '数据可视化' }
      },
      {
        path: '/dashboards',
        name: 'Dashboards',
        component: () => import('../pages/Dashboards.vue'),
        meta: { title: '数据看板' }
      },
      {
        path: '/ai-models',
        name: 'AIModels',
        component: () => import('../pages/AIModels.vue'),
        meta: { title: 'AI模型' }
      },
      {
        path: '/ai-analysis',
        name: 'AIAnalysis',
        component: () => import('../pages/AIAnalysis.vue'),
        meta: { title: 'AI分析' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('../pages/Profile.vue'),
        meta: {requiresAuth: true, title: '个人资料'}
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 所有认证用户都可以访问所有页面
const rolePermissions = {
  admin: ['*'], // 管理员可以访问所有页面和所有操作
  analyst: ['*'], // 数据分析师可以访问所有页面
  viewer: ['*']  // 查看者可以访问所有页面
}

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('🔐 需要认证，跳转到登录页')
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    console.log('🔐 已认证，跳转到首页')
    next('/')
  } else if (to.meta.requiresAuth && authStore.isAuthenticated) {
    const userRole = authStore.user?.role || 'viewer'
    const allowedRoutes = rolePermissions[userRole]

    console.log(`👤 用户角色: ${userRole}, 目标页面: ${to.name}`)

    if (allowedRoutes.includes('*') || allowedRoutes.includes(to.name)) {
      console.log('✅ 权限验证通过')
      next()
    } else {
      console.log('❌ 权限验证失败')
      ElMessage.error('您没有权限访问该页面')
      next('/')
    }
  } else {
    next()
  }
})

export default router
