<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/common/StatCard.vue-->
<template>
  <el-card class="stat-card" :body-style="{ padding: '20px' }" shadow="hover">
    <div class="stat-content">
      <div class="stat-icon" :style="{ backgroundColor: color }">
        <el-icon><component :is="icon" /></el-icon>
      </div>
      <div class="stat-info">
        <div class="stat-value">{{ value }}{{ suffix }}</div>
        <div class="stat-title">{{ title }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: '#409EFF'
  },
  suffix: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
  border: none;
}

.stat-card:hover {
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-title {
  font-size: 14px;
  color: #909399;
}
</style>
