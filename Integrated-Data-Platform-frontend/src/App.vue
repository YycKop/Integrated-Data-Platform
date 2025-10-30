<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/App.vue-->
<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // 应用启动时尝试获取用户信息
  authStore.fetchProfile().catch(() => {
    // 忽略错误，用户可能未登录
  })
})
</script>
