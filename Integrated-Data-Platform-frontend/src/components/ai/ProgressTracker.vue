<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/ai/ProgressTracker.vue-->
<template>
  <div class="progress-tracker">
    <div class="tracker-header">
      <h3 class="tracker-title">{{ title }}</h3>
      <div class="tracker-status">
        <el-tag :type="getStatusTagType" size="small">
          {{ getStatusText }}
        </el-tag>
        <span class="progress-percent">{{ progress }}%</span>
      </div>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar-container">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progress + '%' }"
          :class="getProgressFillClass"
        ></div>
      </div>
    </div>

    <!-- 步骤指示器 -->
    <div class="steps-container">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="step-item"
        :class="getStepClass(index)"
      >
        <div class="step-indicator">
          <div class="step-icon">
            <el-icon v-if="getStepIcon(index)">
              <component :is="getStepIcon(index)" />
            </el-icon>
            <span v-else class="step-number">{{ index + 1 }}</span>
          </div>
          <div class="step-connector" v-if="index < steps.length - 1"></div>
        </div>
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-description">{{ step.description }}</div>
          <div class="step-details" v-if="getStepDetails(index)">
            {{ getStepDetails(index) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 状态信息 -->
    <div class="status-info" v-if="statusMessage">
      <el-alert
        :title="statusMessage"
        :type="getAlertType"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 详细日志 -->
    <div class="detailed-logs" v-if="showLogs && logs.length">
      <el-collapse v-model="activeLogs">
        <el-collapse-item title="详细日志" name="logs">
          <div class="logs-content">
            <div
              v-for="(log, index) in logs"
              :key="index"
              class="log-entry"
              :class="getLogLevelClass(log.level)"
            >
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-level">[{{ log.level }}]</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Check,
  Loading,
  Close,
  Warning,
  InfoFilled
} from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: '进度跟踪'
  },
  progress: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  status: {
    type: String,
    default: 'pending', // pending, running, completed, failed, cancelled
    validator: (value) =>
      ['pending', 'running', 'completed', 'failed', 'cancelled'].includes(value)
  },
  currentStep: {
    type: Number,
    default: 0
  },
  steps: {
    type: Array,
    default: () => []
  },
  statusMessage: {
    type: String,
    default: ''
  },
  showLogs: {
    type: Boolean,
    default: false
  },
  logs: {
    type: Array,
    default: () => []
  }
})

// 响应式数据
const activeLogs = ref(['logs'])

// 计算属性
const getStatusTagType = computed(() => {
  const typeMap = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return typeMap[props.status] || 'info'
})

const getStatusText = computed(() => {
  const textMap = {
    pending: '等待开始',
    running: '进行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return textMap[props.status] || props.status
})

const getProgressFillClass = computed(() => {
  return {
    'progress-fill--completed': props.status === 'completed',
    'progress-fill--failed': props.status === 'failed',
    'progress-fill--cancelled': props.status === 'cancelled'
  }
})

const getAlertType = computed(() => {
  const typeMap = {
    pending: 'info',
    running: 'info',
    completed: 'success',
    failed: 'error',
    cancelled: 'warning'
  }
  return typeMap[props.status] || 'info'
})

// 方法
const getStepClass = (index) => {
  if (props.status === 'failed' && index === props.currentStep) {
    return 'step-item--failed'
  }

  if (index < props.currentStep) {
    return 'step-item--completed'
  } else if (index === props.currentStep) {
    return 'step-item--active'
  } else {
    return 'step-item--pending'
  }
}

const getStepIcon = (index) => {
  if (index < props.currentStep) {
    return Check
  } else if (index === props.currentStep) {
    if (props.status === 'failed') {
      return Close
    } else if (props.status === 'running') {
      return Loading
    }
  }
  return null
}

const getStepDetails = (index) => {
  if (index === props.currentStep && props.statusMessage) {
    return props.statusMessage
  }
  return null
}

const getLogLevelClass = (level) => {
  return `log-entry--${level}`
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.progress-tracker {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tracker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tracker-title {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.tracker-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-percent {
  font-weight: 600;
  color: #409EFF;
  font-size: 14px;
}

.progress-bar-container {
  margin-bottom: 30px;
}

.progress-bar {
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill--completed {
  background: linear-gradient(90deg, #67C23A, #67C23A);
}

.progress-fill--failed {
  background: linear-gradient(90deg, #F56C6C, #F56C6C);
}

.progress-fill--cancelled {
  background: linear-gradient(90deg, #E6A23C, #E6A23C);
}

.steps-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-item {
  display: flex;
  gap: 16px;
  transition: all 0.3s ease;
}

.step-item--completed {
  opacity: 1;
}

.step-item--active {
  opacity: 1;
}

.step-item--pending {
  opacity: 0.6;
}

.step-item--failed {
  opacity: 1;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ebeef5;
  color: #909399;
  font-size: 14px;
  font-weight: 600;
  z-index: 2;
  transition: all 0.3s ease;
}

.step-item--completed .step-icon {
  background: #67C23A;
  color: #fff;
}

.step-item--active .step-icon {
  background: #409EFF;
  color: #fff;
  animation: pulse 2s infinite;
}

.step-item--failed .step-icon {
  background: #F56C6C;
  color: #fff;
}

.step-connector {
  flex: 1;
  width: 2px;
  background: #ebeef5;
  margin: 4px 0;
  transition: all 0.3s ease;
}

.step-item--completed + .step-item--completed .step-connector,
.step-item--completed + .step-item--active .step-connector {
  background: #67C23A;
}

.step-content {
  flex: 1;
  padding-bottom: 20px;
}

.step-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.step-description {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.step-details {
  font-size: 12px;
  color: #409EFF;
  font-style: italic;
}

.status-info {
  margin-top: 20px;
}

.detailed-logs {
  margin-top: 20px;
}

.logs-content {
  max-height: 200px;
  overflow-y: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
}

.log-entry {
  padding: 4px 8px;
  border-left: 3px solid transparent;
  margin-bottom: 2px;
}

.log-entry--info {
  border-left-color: #409EFF;
  background: #f0f7ff;
}

.log-entry--warning {
  border-left-color: #E6A23C;
  background: #fdf6ec;
}

.log-entry--error {
  border-left-color: #F56C6C;
  background: #fef0f0;
}

.log-entry--success {
  border-left-color: #67C23A;
  background: #f0f9ff;
}

.log-time {
  color: #909399;
  margin-right: 8px;
}

.log-level {
  font-weight: 600;
  margin-right: 8px;
}

.log-entry--info .log-level {
  color: #409EFF;
}

.log-entry--warning .log-level {
  color: #E6A23C;
}

.log-entry--error .log-level {
  color: #F56C6C;
}

.log-entry--success .log-level {
  color: #67C23A;
}

.log-message {
  color: #606266;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}
</style>
