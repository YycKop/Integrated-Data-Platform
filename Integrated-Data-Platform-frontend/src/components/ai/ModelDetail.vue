<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/ai/ModelDetail.vue-->
<template>
  <div class="model-detail">
    <div v-if="model" class="detail-content">
      <!-- 基础信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>基础信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">
            {{ model.name }}
          </el-descriptions-item>
          <el-descriptions-item label="模型类型">
            <el-tag :type="getModelTypeTag(model.model_type)">
              {{ getModelTypeText(model.model_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="版本">
            {{ model.version || '1.0' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(model.status)">
              {{ getStatusText(model.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="准确率" :span="2">
            <span v-if="model.accuracy" class="accuracy-value">
              {{ (model.accuracy * 100).toFixed(2) }}%
            </span>
            <span v-else class="text-muted">未训练</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(model.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ model.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 训练配置 -->
      <el-card class="config-card" shadow="never" v-if="model.feature_columns || model.target_column">
        <template #header>
          <div class="card-header">
            <span>训练配置</span>
          </div>
        </template>
        <div class="config-section">
          <div class="config-item">
            <label>特征列:</label>
            <div class="columns-list">
              <el-tag
                v-for="column in model.feature_columns"
                :key="column"
                size="small"
                class="column-tag"
              >
                {{ column }}
              </el-tag>
              <span v-if="!model.feature_columns || model.feature_columns.length === 0" class="text-muted">
                未设置
              </span>
            </div>
          </div>
          <div class="config-item">
            <label>目标列:</label>
            <span class="target-column">{{ model.target_column || '未设置' }}</span>
          </div>
          <div class="config-item" v-if="model.training_config && Object.keys(model.training_config).length > 0">
            <label>训练参数:</label>
            <pre class="config-json">{{ JSON.stringify(model.training_config, null, 2) }}</pre>
          </div>
        </div>
      </el-card>

      <!-- 训练数据 -->
      <el-card class="data-card" shadow="never" v-if="model.training_data">
        <template #header>
          <div class="card-header">
            <span>训练数据</span>
          </div>
        </template>
        <div class="data-info">
          <p>数据集ID: {{ model.training_data }}</p>
          <p v-if="model.training_data_name">数据集名称: {{ model.training_data_name }}</p>
        </div>
      </el-card>

      <!-- 模型文件 -->
      <el-card class="file-card" shadow="never" v-if="model.model_file">
        <template #header>
          <div class="card-header">
            <span>模型文件</span>
          </div>
        </template>
        <div class="file-info">
          <p>模型文件: {{ model.model_file }}</p>
          <el-button type="primary" size="small" @click="downloadModelFile">
            下载模型
          </el-button>
        </div>
      </el-card>
    </div>

    <div v-else class="no-data">
      <el-empty description="模型信息加载失败" />
    </div>

    <div class="detail-actions">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="handleEdit">编辑模型</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  model: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'edit'])

const getModelTypeText = (type) => {
  const types = {
    'price_prediction': '价格预测',
    'yield_prediction': '产量预测',
    'disease_detection': '病害检测',
    'market_analysis': '市场分析'
  }
  return types[type] || type
}

const getModelTypeTag = (type) => {
  const tags = {
    'price_prediction': 'success',
    'yield_prediction': 'warning',
    'disease_detection': 'danger',
    'market_analysis': 'info'
  }
  return tags[type] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'training': '训练中',
    'active': '已激活',
    'inactive': '未激活',
    'error': '错误'
  }
  return statusMap[status] || status
}

const getStatusTag = (status) => {
  const tags = {
    'training': 'warning',
    'active': 'success',
    'inactive': 'info',
    'error': 'danger'
  }
  return tags[status] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const downloadModelFile = () => {
  ElMessage.info('模型下载功能开发中')
}

const handleEdit = () => {
  emit('edit', props.model)
  emit('close')
}
</script>

<style scoped>
.model-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.config-item label {
  font-weight: 500;
  min-width: 80px;
  color: #606266;
}

.columns-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.column-tag {
  margin: 2px;
}

.target-column {
  background: #f4f4f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
}

.config-json {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.data-info, .file-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.accuracy-value {
  color: #67c23a;
  font-weight: 600;
  font-size: 16px;
}

.text-muted {
  color: #909399;
  font-style: italic;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

.no-data {
  text-align: center;
  padding: 40px 0;
}
</style>
