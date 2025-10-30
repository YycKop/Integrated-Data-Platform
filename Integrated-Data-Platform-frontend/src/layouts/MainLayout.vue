<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/layouts/MainLayout.vue-->
<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo">
            <h2>一体化数据平台</h2>
          </div>
        </div>

        <div class="nav-section">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            router
            class="header-menu"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span class="menu-text">首页</span>
            </el-menu-item>
            <el-menu-item index="/data-sources">
              <el-icon><DataLine /></el-icon>
              <span class="menu-text">数据源</span>
            </el-menu-item>
            <el-menu-item index="/datasets">
              <el-icon><Collection /></el-icon>
              <span class="menu-text">数据集</span>
            </el-menu-item>
            <el-menu-item index="/processing">
              <el-icon><SetUp /></el-icon>
              <span class="menu-text">数据处理</span>
            </el-menu-item>
            <el-menu-item index="/visualization">
              <el-icon><DataAnalysis /></el-icon>
              <span class="menu-text">可视化</span>
            </el-menu-item>
            <el-menu-item index="/dashboards">
              <el-icon><Monitor /></el-icon>
              <span class="menu-text">数据看板</span>
            </el-menu-item>
            <!-- AI相关菜单 -->
            <el-menu-item index="/ai-models">
              <el-icon><Cpu /></el-icon>
              <span class="menu-text">AI模型</span>
            </el-menu-item>
            <el-menu-item index="/ai-analysis">
              <el-icon><Opportunity /></el-icon>
              <span class="menu-text">智能分析</span>
            </el-menu-item>
            <!-- 已移除预测结果菜单 -->
          </el-menu>
        </div>

        <div class="user-section">
          <el-dropdown @command="handleCommand" trigger="click">
            <span class="user-dropdown">
              <el-avatar :size="32" class="user-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ authStore.user?.username }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <el-main class="layout-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import {computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAuthStore} from '../stores/auth'
import {ElMessage, ElMessageBox} from 'element-plus'

// 导入图标 - 使用element-plus提供的标准图标
import {
  House,
  DataLine,
  Collection,
  SetUp,
  DataAnalysis,
  Monitor,
  User,
  ArrowDown,
  SwitchButton,
  Cpu,
  Opportunity
  // 移除 TrendCharts 图标导入
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await authStore.logout()
      router.push('/login')
      ElMessage.success('退出成功')
    } catch (error) {
      // 用户取消退出
    }
  } else if (command === 'profile') {
    router.push('/profile') // 跳转到个人信息页面
  }
}
</script>

<style scoped>
/* 保持原有的样式不变 */
.layout-container {
  height: 100vh;
  min-width: 1280px;
}

.layout-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  padding: 0;
  height: 60px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 20px;
  min-width: 1280px;
}

.logo-section {
  flex-shrink: 0;
  min-width: 160px;
  max-width: 160px;
}

.logo h2 {
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.nav-section {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 800px;
  max-width: 900px;
  margin: 0 20px;
}

.header-menu {
  border-bottom: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-width: 100%;
}

.header-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.9);
  background: transparent !important;
  border-bottom: 2px solid transparent;
  padding: 0 12px !important;
  height: 60px;
  line-height: 60px;
  margin: 0 1px !important;
  min-width: auto;
  flex: 1;
  max-width: 140px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.header-menu .el-menu-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1) !important;
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.header-menu .el-menu-item.is-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.15) !important;
  border-bottom-color: #fff;
  font-weight: 500;
}

.header-menu .el-menu-item .el-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.menu-text {
  white-space: nowrap;
  font-size: 14px;
  flex-shrink: 0;
}

.user-section {
  flex-shrink: 0;
  min-width: 140px;
  max-width: 160px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 20px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-dropdown:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.user-avatar {
  background: linear-gradient(45deg, #ff6b6b, #feca57);
  flex-shrink: 0;
}

.username {
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  max-width: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-arrow {
  color: #fff;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.user-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.layout-main {
  padding: 0;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  overflow: auto;
}

:deep(.el-menu--horizontal) {
  border-bottom: none !important;
}

::v-deep(.el-menu--horizontal) > .el-menu-item {
  border-bottom: none !important;
}

:deep(.el-menu--horizontal .el-menu-item:not(.is-disabled):focus) {
  background-color: transparent !important;
}

:deep(.el-menu--horizontal .el-menu-item:not(.is-disabled):hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-dropdown-menu) {
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 14px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}

@media screen and (max-width: 1400px) {
  .layout-container {
    min-width: 1200px;
  }

  .header-content {
    min-width: 1200px;
    padding: 0 16px;
  }

  .nav-section {
    min-width: 700px;
    max-width: 800px;
  }

  .header-menu .el-menu-item {
    padding: 0 10px !important;
  }

  .menu-text {
    font-size: 13px;
  }

  .logo h2 {
    font-size: 16px;
  }
}

@media screen and (max-width: 1280px) {
  .layout-container {
    min-width: 1150px;
  }

  .header-content {
    min-width: 1150px;
    padding: 0 12px;
  }

  .nav-section {
    min-width: 650px;
    max-width: 750px;
  }

  .header-menu .el-menu-item {
    padding: 0 8px !important;
    max-width: 120px;
  }

  .menu-text {
    font-size: 12px;
  }

  .logo-section {
    min-width: 140px;
    max-width: 140px;
  }

  .user-section {
    min-width: 120px;
    max-width: 140px;
  }
}

@media screen and (max-width: 1150px) {
  .layout-container {
    min-width: 1100px;
  }

  .header-content {
    min-width: 1100px;
    padding: 0 10px;
  }

  .nav-section {
    min-width: 600px;
    max-width: 700px;
  }

  .header-menu .el-menu-item {
    padding: 0 6px !important;
    max-width: 110px;
  }

  .menu-text {
    font-size: 12px;
  }

  .header-menu .el-menu-item .el-icon {
    font-size: 14px;
  }
}
</style>
