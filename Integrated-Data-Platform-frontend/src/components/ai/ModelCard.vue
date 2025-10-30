<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/ai/ModelCard.vue-->
<template>
  <el-card class="model-card" shadow="hover" :body-style="{ padding: '0' }">
    <!-- 卡片头部 -->
    <div class="card-header" :class="getHeaderClass">
      <div class="header-content">
        <div class="model-icon">
          <el-icon :size="24" :color="getIconColor">
            <component :is="getModelIcon" />
          </el-icon>
        </div>
        <div class="model-info">
          <h3 class="model-name" :title="model.name">{{ model.name }}</h3>
          <div class="model-meta">
            <span class="model-version">v{{ model.version }}</span>
            <el-tag :type="getStatusTagType" size="small" effect="light">
              {{ getStatusText }}
            </el-tag>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <el-dropdown trigger="click" @command="handleHeaderCommand">
          <el-button link class="more-button">
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="view">
                <el-icon><View /></el-icon>
                查看详情
              </el-dropdown-item>
              <el-dropdown-item command="edit">
                <el-icon><Edit /></el-icon>
                编辑模型
              </el-dropdown-item>
              <el-dropdown-item command="clone" divided>
                <el-icon><CopyDocument /></el-icon>
                克隆模型
              </el-dropdown-item>
              <el-dropdown-item command="export">
                <el-icon><Download /></el-icon>
                导出模型
              </el-dropdown-item>
              <el-dropdown-item command="delete" divided class="delete-item">
                <el-icon><Delete /></el-icon>
                删除模型
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 模型描述 -->
      <div class="model-description" v-if="model.description">
        <p>{{ model.description }}</p>
      </div>

      <!-- 模型指标 -->
      <div class="model-metrics">
        <div class="metric-item">
          <div class="metric-label">准确率</div>
          <div class="metric-value">
            <el-progress
              v-if="model.accuracy"
              :percentage="Math.round(model.accuracy * 100)"
              :stroke-width="8"
              :show-text="false"
              :color="getAccuracyColor"
            />
            <span class="accuracy-text" :class="getAccuracyTextClass">
              {{ formatAccuracy(model.accuracy) }}
            </span>
          </div>
        </div>

        <div class="metric-item">
          <div class="metric-label">训练数据</div>
          <div class="metric-value">
            <el-text type="info" size="small">
              {{ model.training_data?.name || '未设置' }}
            </el-text>
          </div>
        </div>

        <div class="metric-item">
          <div class="metric-label">特征数量</div>
          <div class="metric-value">
            <el-tag size="small" effect="plain">
              {{ model.feature_columns?.length || 0 }} 个
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 训练配置摘要 -->
      <div class="training-summary" v-if="model.training_config">
        <el-divider content-position="left">训练配置</el-divider>
        <div class="config-items">
          <div class="config-item">
            <span class="config-label">训练轮次:</span>
            <span class="config-value">{{ model.training_config.n_estimators || 100 }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">最大深度:</span>
            <span class="config-value">{{ model.training_config.max_depth || 10 }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">测试比例:</span>
            <span class="config-value">{{ (model.training_config.test_size || 0.2) * 100 }}%</span>
          </div>
        </div>
      </div>

      <!-- 特征重要性 (前3个) -->
      <div class="feature-importance" v-if="showFeatureImportance && topFeatures.length">
        <el-divider content-position="left">关键特征</el-divider>
        <div class="features-list">
          <div
            v-for="(feature, index) in topFeatures"
            :key="feature.name"
            class="feature-item"
          >
            <div class="feature-rank">
              <el-tag size="small" :type="getRankTagType(index)">
                #{{ index + 1 }}
              </el-tag>
            </div>
            <div class="feature-name" :title="feature.name">
              {{ feature.name }}
            </div>
            <div class="feature-score">
              {{ (feature.importance * 100).toFixed(1) }}%
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer">
      <div class="footer-left">
        <el-text type="info" size="small">
          {{ formatTime(model.created_at) }}
        </el-text>
      </div>

      <div class="footer-right">
        <el-button
          size="small"
          :type="canTrain ? 'primary' : 'info'"
          :disabled="!canTrain"
          @click="handleTrain"
          :loading="trainingLoading"
        >
          <template #loading>
            <el-icon class="is-loading"><Loading /></el-icon>
            训练中
          </template>
          <template v-else>
            <el-icon><VideoPlay /></el-icon>
            {{ getTrainButtonText }}
          </template>
        </el-button>

        <el-button
          size="small"
          :type="canPredict ? 'success' : 'info'"
          :disabled="!canPredict"
          @click="handlePredict"
        >
          <el-icon><TrendCharts /></el-icon>
          预测
        </el-button>
      </div>
    </div>

    <!-- 训练状态指示器 -->
    <div class="training-indicator" v-if="model.status === 'training'">
      <div class="indicator-pulse"></div>
      <span class="indicator-text">训练中...</span>
    </div>
  </el-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  MoreFilled,
  View,
  Edit,
  CopyDocument,
  Download,
  Delete,
  VideoPlay,
  TrendCharts,
  Loading,
  Cpu,
  DataAnalysis,
  Warning,
  Monitor
} from '@element-plus/icons-vue'

const props = defineProps({
  model: {
    type: Object,
    required: true,
    validator: (value) => {
      // 验证模型对象的结构
      return value && typeof value === 'object' && 'name' in value
    }
  },
  showFeatureImportance: {
    type: Boolean,
    default: true
  },
  maxFeatures: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits([
  'view',
  'edit',
  'clone',
  'export',
  'delete',
  'train',
  'predict'
])

// 响应式数据
const trainingLoading = ref(false)

// 计算属性
const getModelIcon = computed(() => {
  const iconMap = {
    'price_prediction': TrendCharts,
    'yield_prediction': DataAnalysis,
    'disease_detection': Warning,
    'market_analysis': Monitor,
    'climate_impact': Cpu
  }
  return iconMap[props.model.model_type] || Cpu
})

const getIconColor = computed(() => {
  const colorMap = {
    'price_prediction': '#67C23A',
    'yield_prediction': '#E6A23C',
    'disease_detection': '#F56C6C',
    'market_analysis': '#409EFF',
    'climate_impact': '#909399'
  }
  return colorMap[props.model.model_type] || '#409EFF'
})

const getHeaderClass = computed(() => {
  return `header--${props.model.model_type}`
})

// 修复状态显示逻辑
const getStatusTagType = computed(() => {
  console.log('模型状态:', props.model.status, '模型:', props.model.name)

  const status = props.model.status || 'inactive'
  const typeMap = {
    'active': 'success',
    'training': 'warning',
    'inactive': 'info',
    'error': 'danger'
  }
  return typeMap[status] || 'info'
})

const getStatusText = computed(() => {
  const status = props.model.status || 'inactive'
  const textMap = {
    'active': '已激活',
    'training': '训练中',
    'inactive': '未激活',
    'error': '错误'
  }
  return textMap[status] || status
})

const getAccuracyColor = computed(() => {
  const accuracy = props.model.accuracy
  if (!accuracy) return '#909399'

  if (accuracy >= 0.9) return '#67C23A'
  if (accuracy >= 0.7) return '#E6A23C'
  if (accuracy >= 0.5) return '#F56C6C'
  return '#909399'
})

const getAccuracyTextClass = computed(() => {
  const accuracy = props.model.accuracy
  if (!accuracy) return 'accuracy-text--unknown'

  if (accuracy >= 0.9) return 'accuracy-text--high'
  if (accuracy >= 0.7) return 'accuracy-text--medium'
  if (accuracy >= 0.5) return 'accuracy-text--low'
  return 'accuracy-text--poor'
})

const canTrain = computed(() => {
  const status = props.model.status || 'inactive'
  return status !== 'training' && props.model.training_data
})

const canPredict = computed(() => {
  const status = props.model.status || 'inactive'
  return status === 'active'
})

const getTrainButtonText = computed(() => {
  const status = props.model.status || 'inactive'
  if (status === 'training') return '训练中'
  if (!props.model.training_data) return '需配置数据'
  return '训练'
})

const topFeatures = computed(() => {
  if (!props.model.feature_importance) return []

  const features = Object.entries(props.model.feature_importance)
    .map(([name, importance]) => ({ name, importance }))
    .sort((a, b) => b.importance - a.importance)
    .slice(0, props.maxFeatures)

  return features
})

// 方法
const formatAccuracy = (accuracy) => {
  if (accuracy === null || accuracy === undefined) return '未训练'
  return `${(accuracy * 100).toFixed(1)}%`
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    return '今天'
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

const getRankTagType = (index) => {
  const types = ['danger', 'warning', 'primary', 'success', 'info']
  return types[index] || 'info'
}

const handleHeaderCommand = async (command) => {
  switch (command) {
    case 'view':
      emit('view', props.model)
      break
    case 'edit':
      emit('edit', props.model)
      break
    case 'clone':
      emit('clone', props.model)
      break
    case 'export':
      emit('export', props.model)
      break
    case 'delete':
      await handleDelete()
      break
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${props.model.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    emit('delete', props.model)
    ElMessage.success('模型删除成功')
  } catch (error) {
    // 用户取消删除
  }
}

const handleTrain = async () => {
  if (!canTrain.value) {
    if (!props.model.training_data) {
      ElMessage.warning('请先配置训练数据')
    }
    return
  }

  trainingLoading.value = true
  try {
    await emit('train', props.model)
  } catch (error) {
    ElMessage.error('训练启动失败')
  } finally {
    trainingLoading.value = false
  }
}

const handlePredict = () => {
  if (!canPredict.value) {
    ElMessage.warning('模型未激活，无法进行预测')
    return
  }
  emit('predict', props.model)
}
</script>

<style scoped>
.model-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
}

.model-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 卡片头部样式 */
.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
}

.header--price_prediction {
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
}

.header--yield_prediction {
  background: linear-gradient(135deg, #E6A23C 0%, #EBB563 100%);
}

.header--disease_detection {
  background: linear-gradient(135deg, #F56C6C 0%, #F78989 100%);
}

.header--market_analysis {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
}

.header--climate_impact {
  background: linear-gradient(135deg, #909399 0%, #A6A9AD 100%);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.model-info {
  flex: 1;
}

.model-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.model-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-version {
  font-size: 12px;
  opacity: 0.8;
}

.header-actions {
  position: absolute;
  top: 16px;
  right: 16px;
}

.more-button {
  color: white;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.more-button:hover {
  opacity: 1;
}

:deep(.delete-item) {
  color: #F56C6C;
}

:deep(.delete-item .el-icon) {
  color: #F56C6C;
}

/* 卡片内容样式 */
.card-content {
  padding: 20px;
}

.model-description {
  margin-bottom: 16px;
}

.model-description p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.model-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
}

.metric-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.accuracy-text {
  font-size: 13px;
  font-weight: 600;
  min-width: 50px;
  text-align: right;
}

.accuracy-text--high {
  color: #67C23A;
}

.accuracy-text--medium {
  color: #E6A23C;
}

.accuracy-text--low {
  color: #F56C6C;
}

.accuracy-text--poor {
  color: #909399;
}

.accuracy-text--unknown {
  color: #C0C4CC;
  font-style: italic;
}

.training-summary {
  margin-bottom: 16px;
}

.config-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.config-label {
  color: #909399;
}

.config-value {
  color: #606266;
  font-weight: 500;
}

.feature-importance {
  margin-bottom: 8px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: #f8f9fa;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.feature-item:hover {
  background: #f0f2f5;
}

.feature-rank {
  flex-shrink: 0;
}

.feature-name {
  flex: 1;
  font-size: 13px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.feature-score {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  flex-shrink: 0;
}

/* 卡片底部样式 */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-top: 1px solid #ebeef5;
}

.footer-left {
  flex: 1;
}

.footer-right {
  display: flex;
  gap: 8px;
}

/* 训练状态指示器 */
.training-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(230, 162, 60, 0.95);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  backdrop-filter: blur(10px);
}

.indicator-pulse {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.indicator-text {
  font-weight: 500;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(0.8);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    padding: 16px;
  }

  .card-content {
    padding: 16px;
  }

  .card-footer {
    padding: 12px 16px;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .footer-right {
    justify-content: space-between;
  }

  .model-metrics {
    gap: 10px;
  }

  .metric-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .metric-value {
    width: 100%;
    justify-content: space-between;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .model-card {
    background: #1f1f1f;
    border-color: #434343;
  }

  .card-footer {
    background: #141414;
    border-color: #434343;
  }

  .feature-item {
    background: #262626;
  }

  .feature-item:hover {
    background: #2f2f2f;
  }

  .model-description p {
    color: #d9d9d9;
  }

  .config-value {
    color: #d9d9d9;
  }

  .feature-name {
    color: #d9d9d9;
  }
}
</style>
