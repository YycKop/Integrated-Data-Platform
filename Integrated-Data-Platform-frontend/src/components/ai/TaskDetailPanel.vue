<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/ai/TaskDetailPanel.vue-->
<template>
  <div class="task-detail-panel">
    <!-- 基本信息 -->
    <el-card class="info-card">
      <template #header>
        <span>基本信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务名称">{{ task.name }}</el-descriptions-item>
        <el-descriptions-item label="任务类型">{{ getTaskTypeText(task.task_type) }}</el-descriptions-item>
        <el-descriptions-item label="关联模型">{{ task.ai_model_name }}</el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <el-tag :type="getStatusTagType(task.status)">
            {{ getStatusText(task.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(task.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatDate(task.completed_at) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="进度" :span="2">
          <el-progress
            :percentage="Math.round(task.progress)"
            :status="getProgressStatus(task.status)"
            :show-text="true"
          />
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 输入参数 -->
    <el-card class="params-card" v-if="task.input_parameters">
      <template #header>
        <span>输入参数</span>
      </template>
      <el-collapse>
        <el-collapse-item title="查看参数详情">
          <pre class="json-view">{{ JSON.stringify(task.input_parameters, null, 2) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 输出结果 -->
    <el-card class="result-card" v-if="task.output_result">
      <template #header>
        <span>输出结果</span>
        <el-button
          v-if="task.output_result"
          type="primary"
          size="small"
          @click="downloadResult"
          style="float: right;"
        >
          <el-icon><Download /></el-icon>
          下载结果
        </el-button>
      </template>

      <div v-if="task.task_type === 'model_training'">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="训练准确率">
            {{ (task.output_result.accuracy * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="训练耗时">
            {{ task.output_result.training_time }} 秒
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="task.output_result.feature_importance" class="feature-importance">
          <h4>特征重要性</h4>
          <el-table
            :data="featureImportanceData"
            size="small"
            max-height="200"
          >
            <el-table-column prop="feature" label="特征名称" />
            <el-table-column prop="importance" label="重要性" width="120">
              <template #default="{ row }">
                {{ (row.importance * 100).toFixed(2) }}%
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div v-else-if="task.task_type.includes('prediction')">
        <el-alert
          title="预测完成"
          :description="`共处理 ${task.output_result.processed_count} 条数据，平均置信度 ${(task.output_result.average_confidence * 100).toFixed(1)}%`"
          type="success"
          :closable="false"
          style="margin-bottom: 16px;"
        />

        <el-collapse>
          <el-collapse-item title="查看预测结果样本">
            <el-table
              :data="predictionSamples"
              size="small"
              max-height="300"
            >
              <el-table-column
                v-for="column in predictionColumns"
                :key="column"
                :prop="column"
                :label="column"
                min-width="100"
              />
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <!-- 错误信息 -->
    <el-card class="error-card" v-if="task.error_message">
      <template #header>
        <span style="color: #F56C6C;">错误信息</span>
      </template>
      <el-alert
        :title="task.error_message"
        type="error"
        :closable="false"
        show-icon
      />
    </el-card>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button
        v-if="task.status === 'failed'"
        type="primary"
        @click="retryTask"
      >
        重试任务
      </el-button>
      <el-button
        v-if="task.status === 'running'"
        type="warning"
        @click="cancelTask"
      >
        取消任务
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

// 计算属性
const featureImportanceData = computed(() => {
  if (!props.task.output_result?.feature_importance) return []

  return Object.entries(props.task.output_result.feature_importance)
    .map(([feature, importance]) => ({ feature, importance }))
    .sort((a, b) => b.importance - a.importance)
})

const predictionSamples = computed(() => {
  if (!props.task.output_result?.predictions) return []
  return props.task.output_result.predictions.slice(0, 5) // 只显示前5条样本
})

const predictionColumns = computed(() => {
  if (predictionSamples.value.length === 0) return []
  return Object.keys(predictionSamples.value[0])
})

// 方法
const getTaskTypeText = (type) => {
  const typeMap = {
    'batch_prediction': '批量预测',
    'realtime_prediction': '实时预测',
    'model_training': '模型训练'
  }
  return typeMap[type] || type
}

const getStatusTagType = (status) => {
  const typeMap = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '待处理',
    running: '进行中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || status
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return null
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const downloadResult = () => {
  ElMessage.info('下载功能开发中')
}

const retryTask = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重试这个任务吗？',
      '确认重试',
      { type: 'warning' }
    )
    // 调用重试API
    ElMessage.success('任务重试请求已发送')
  } catch (error) {
    // 用户取消操作
  }
}

const cancelTask = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消这个任务吗？',
      '确认取消',
      { type: 'warning' }
    )
    // 调用取消API
    ElMessage.success('任务取消请求已发送')
  } catch (error) {
    // 用户取消操作
  }
}
</script>

<style scoped>
.task-detail-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 70vh;
  overflow-y: auto;
}

.info-card,
.params-card,
.result-card,
.error-card {
  margin-bottom: 0;
}

.json-view {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
}

.feature-importance {
  margin-top: 16px;
}

.feature-importance h4 {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
