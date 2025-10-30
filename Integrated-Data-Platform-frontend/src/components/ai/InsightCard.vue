<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/ai/InsightCard.vue-->
<template>
  <el-card class="insight-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-icon :color="getInsightColor" class="insight-icon">
            <component :is="getInsightIcon" />
          </el-icon>
          <span class="insight-title">{{ insight.title || '数据洞察' }}</span>
          <el-tag :type="getInsightTagType" size="small">
            {{ getInsightTypeText }}
          </el-tag>
        </div>
        <div class="header-right">
          <el-button link @click="handleCopy" title="复制内容">
            <el-icon><DocumentCopy /></el-icon>
          </el-button>
          <el-button link @click="handleDelete" title="删除洞察">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </template>

    <div class="insight-content">
      <div class="insight-text" v-if="insight.text">
        {{ insight.text }}
      </div>

      <div class="insight-metrics" v-if="insight.metrics">
        <div class="metrics-grid">
          <div
            v-for="(value, key) in insight.metrics"
            :key="key"
            class="metric-item"
          >
            <div class="metric-label">{{ formatMetricLabel(key) }}</div>
            <div class="metric-value">{{ formatMetricValue(value) }}</div>
          </div>
        </div>
      </div>

      <div class="insight-chart" v-if="insight.chart_data">
        <div class="mini-chart">
          <div class="chart-placeholder">
            <el-icon><TrendCharts /></el-icon>
            <span>可视化图表</span>
          </div>
        </div>
      </div>

      <div class="insight-recommendations" v-if="insight.recommendations">
        <el-divider content-position="left">建议措施</el-divider>
        <ul class="recommendations-list">
          <li
            v-for="(recommendation, index) in insight.recommendations"
            :key="index"
            class="recommendation-item"
          >
            <el-icon color="#67C23A"><Check /></el-icon>
            <span>{{ recommendation }}</span>
          </li>
        </ul>
      </div>

      <div class="insight-tags" v-if="insight.tags && insight.tags.length">
        <el-tag
          v-for="tag in insight.tags"
          :key="tag"
          size="small"
          class="insight-tag"
        >
          {{ tag }}
        </el-tag>
      </div>
    </div>

    <template #footer>
      <div class="card-footer">
        <div class="footer-left">
          <span class="timestamp">{{ formatTimestamp(insight.timestamp) }}</span>
          <span class="confidence" v-if="insight.confidence">
            置信度: {{ (insight.confidence * 100).toFixed(0) }}%
          </span>
        </div>
        <div class="footer-right">
          <el-button link @click="handleLike" :class="{ liked: insight.liked }">
            <el-icon><Star /></el-icon>
            {{ insight.likes || 0 }}
          </el-button>
        </div>
      </div>
    </template>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DocumentCopy,
  Delete,
  TrendCharts,
  Check,
  Star,
  Warning,
  SuccessFilled,
  InfoFilled,
  Opportunity
} from '@element-plus/icons-vue'

const props = defineProps({
  insight: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['delete', 'like'])

// 计算属性
const getInsightType = computed(() => {
  return props.insight.type || 'info'
})

const getInsightIcon = computed(() => {
  const iconMap = {
    warning: Warning,
    success: SuccessFilled,
    danger: Warning,
    info: InfoFilled,
    opportunity: Opportunity
  }
  return iconMap[getInsightType.value] || InfoFilled
})

const getInsightColor = computed(() => {
  const colorMap = {
    warning: '#E6A23C',
    success: '#67C23A',
    danger: '#F56C6C',
    info: '#409EFF',
    opportunity: '#F56C6C'
  }
  return colorMap[getInsightType.value] || '#409EFF'
})

const getInsightTagType = computed(() => {
  const typeMap = {
    warning: 'warning',
    success: 'success',
    danger: 'danger',
    info: 'info',
    opportunity: 'danger'
  }
  return typeMap[getInsightType.value] || 'info'
})

const getInsightTypeText = computed(() => {
  const textMap = {
    warning: '预警',
    success: '积极',
    danger: '风险',
    info: '信息',
    opportunity: '机会'
  }
  return textMap[getInsightType.value] || '洞察'
})

// 方法
const handleCopy = () => {
  const textToCopy = props.insight.text || JSON.stringify(props.insight, null, 2)

  navigator.clipboard.writeText(textToCopy).then(() => {
    ElMessage.success('内容已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const handleDelete = () => {
  emit('delete', props.insight)
}

const handleLike = () => {
  emit('like', props.insight)
}

const formatMetricLabel = (label) => {
  const labelMap = {
    'accuracy': '准确率',
    'precision': '精确率',
    'recall': '召回率',
    'f1_score': 'F1分数',
    'mae': '平均绝对误差',
    'mse': '均方误差',
    'rmse': '均方根误差',
    'r2': 'R²分数'
  }
  return labelMap[label] || label
}

const formatMetricValue = (value) => {
  if (typeof value === 'number') {
    if (value < 1 && value > 0) {
      return (value * 100).toFixed(1) + '%'
    }
    return value.toFixed(4)
  }
  return value
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.insight-card {
  margin-bottom: 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.insight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.insight-icon {
  font-size: 18px;
}

.insight-title {
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 4px;
}

.insight-content {
  min-height: 100px;
}

.insight-text {
  line-height: 1.6;
  color: #606266;
  margin-bottom: 16px;
}

.insight-metrics {
  margin-bottom: 16px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.metric-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  text-align: center;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.insight-chart {
  margin-bottom: 16px;
}

.mini-chart {
  height: 80px;
  background: #f8f9fa;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.insight-recommendations {
  margin-bottom: 16px;
}

.recommendations-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  line-height: 1.5;
}

.recommendation-item .el-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.insight-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.insight-tag {
  margin: 2px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.footer-left {
  display: flex;
  gap: 16px;
}

.footer-right .liked {
  color: #E6A23C;
}

.footer-right .liked .el-icon {
  color: #E6A23C;
}
</style>
