<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/common/LoadingSpinner.vue-->
<template>
  <div class="loading-spinner" :class="spinnerClasses">
    <!-- 大型加载动画 -->
    <div v-if="size === 'large'" class="spinner-large">
      <div class="spinner-circle">
        <div class="spinner-inner"></div>
      </div>
      <div class="spinner-text" v-if="text">{{ text }}</div>
    </div>

    <!-- 中型加载动画 -->
    <div v-else-if="size === 'medium'" class="spinner-medium">
      <div class="spinner-dots">
        <div class="dot dot-1"></div>
        <div class="dot dot-2"></div>
        <div class="dot dot-3"></div>
      </div>
      <div class="spinner-text" v-if="text">{{ text }}</div>
    </div>

    <!-- 小型加载动画 (默认) -->
    <div v-else class="spinner-small">
      <div class="spinner-ring" :style="spinnerStyle"></div>
      <div class="spinner-text" v-if="text">{{ text }}</div>
    </div>

    <!-- 进度条加载 -->
    <div v-if="type === 'progress'" class="spinner-progress">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progress + '%' }"
        ></div>
      </div>
      <div class="progress-text" v-if="showProgressText">
        {{ progress }}%
      </div>
    </div>

    <!-- 骨架屏加载 -->
    <div v-if="type === 'skeleton'" class="spinner-skeleton">
      <div class="skeleton-header" v-if="skeletonConfig.showHeader"></div>
      <div class="skeleton-content">
        <div
          v-for="i in skeletonConfig.lines"
          :key="i"
          class="skeleton-line"
          :style="getSkeletonLineStyle(i)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 加载类型
  type: {
    type: String,
    default: 'spinner', // spinner, progress, skeleton
    validator: (value) => ['spinner', 'progress', 'skeleton'].includes(value)
  },

  // 尺寸
  size: {
    type: String,
    default: 'small', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },

  // 颜色
  color: {
    type: String,
    default: '#409EFF'
  },

  // 加载文本
  text: {
    type: String,
    default: ''
  },

  // 进度 (仅对progress类型有效)
  progress: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },

  // 是否显示进度文本
  showProgressText: {
    type: Boolean,
    default: true
  },

  // 是否居中显示
  center: {
    type: Boolean,
    default: true
  },

  // 是否全屏显示
  fullscreen: {
    type: Boolean,
    default: false
  },

  // 背景颜色
  background: {
    type: String,
    default: 'rgba(255, 255, 255, 0.9)'
  },

  // 骨架屏配置
  skeletonConfig: {
    type: Object,
    default: () => ({
      lines: 3,
      showHeader: true,
      lineHeight: 16,
      spacing: 12
    })
  }
})

// 计算属性
const spinnerClasses = computed(() => ({
  'loading-spinner--center': props.center,
  'loading-spinner--fullscreen': props.fullscreen,
  [`loading-spinner--${props.type}`]: true
}))

const spinnerStyle = computed(() => ({
  borderColor: `${props.color} transparent transparent transparent`
}))

// 方法
const getSkeletonLineStyle = (index) => {
  const isHeader = index === 1 && props.skeletonConfig.showHeader
  const width = isHeader ? '60%' : `${80 - (index - 1) * 10}%`

  return {
    height: `${props.skeletonConfig.lineHeight}px`,
    marginBottom: `${props.skeletonConfig.spacing}px`,
    width: width
  }
}
</script>

<style scoped>
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: v-bind(background);
  transition: all 0.3s ease;
}

.loading-spinner--center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2000;
}

.loading-spinner--fullscreen {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 9999;
}

/* 大型加载动画 */
.spinner-large {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner-circle {
  width: 60px;
  height: 60px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid v-bind(color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  position: relative;
}

.spinner-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  border: 2px solid #f3f3f3;
  border-radius: 50%;
}

.spinner-text {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

/* 中型加载动画 - 点状 */
.spinner-medium {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: v-bind(color);
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot-1 {
  animation-delay: -0.32s;
}

.dot-2 {
  animation-delay: -0.16s;
}

.dot-3 {
  animation-delay: 0s;
}

/* 小型加载动画 - 环形 */
.spinner-small {
  display: flex;
  align-items: center;
  gap: 12px;
}

.spinner-ring {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid v-bind(color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  border-top-color: transparent;
  border-right-color: transparent;
}

/* 进度条加载 */
.spinner-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 200px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: #ebeef5;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, v-bind(color), v-bind(color));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

/* 骨架屏加载 */
.spinner-skeleton {
  width: 100%;
  max-width: 400px;
}

.skeleton-header {
  height: 20px;
  background: linear-gradient(90deg, #f2f2f2 25%, #e6e6e6 50%, #f2f2f2 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  margin-bottom: 16px;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
}

.skeleton-line {
  background: linear-gradient(90deg, #f2f2f2 25%, #e6e6e6 50%, #f2f2f2 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: skeleton-loading 1.5s infinite;
}

/* 动画定义 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .spinner-large {
    gap: 16px;
  }

  .spinner-circle {
    width: 50px;
    height: 50px;
    border-width: 3px;
  }

  .spinner-inner {
    width: 30px;
    height: 30px;
    border-width: 1px;
  }

  .spinner-text {
    font-size: 14px;
  }

  .spinner-progress {
    width: 160px;
  }
}
</style>
