// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/router/index.js
import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '../stores/auth'

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
        component: () => import('../pages/Dashboard.vue')
      },
      {
        path: '/datasets',
        name: 'Datasets',
        component: () => import('../pages/Datasets.vue')
      },
      {
        path: '/data-sources',
        name: 'DataSources',
        component: () => import('../pages/DataSources.vue')
      },
      {
        path: '/processing',
        name: 'Processing',
        component: () => import('../pages/Processing.vue')
      },
      {
        path: '/visualization',
        name: 'Visualization',
        component: () => import('../pages/Visualization.vue')
      },
      {
        path: '/dashboards',
        name: 'Dashboards',
        component: () => import('../pages/Dashboards.vue')
      },
      {
        path: '/ai-models',
        name: 'AIModels',
        component: () => import('../pages/AIModels.vue')
      },
      {
        path: '/ai-analysis',
        name: 'AIAnalysis',
        component: () => import('../pages/AIAnalysis.vue')
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('../pages/Profile.vue'),
        meta: {requiresAuth: true}
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
