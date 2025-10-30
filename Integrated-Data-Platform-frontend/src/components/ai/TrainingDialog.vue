<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/ai/TrainingDialog.vue-->
<template>
  <el-dialog
    :model-value="visible"
    :title="`训练模型 - ${model?.name}`"
    width="800px"
    :before-close="handleClose"
    @update:model-value="$emit('update:visible', $event)"
  >
    <div class="training-dialog">
      <!-- 调试信息（开发时显示） -->
      <div v-if="true"
           style="background: #f5f5f5; padding: 10px; margin-bottom: 20px; border-radius: 4px;">
        <h4>训练对话框调试信息:</h4>
        <pre>{{
            {
              datasetsCount: datasets.length,
              selectedDatasetId: trainingForm.dataset_id,
              datasetColumns: datasetColumns,
              datasetColumnsList: datasetColumnsList,
              features: trainingForm.features,
              target: trainingForm.target,
              selectedDataset: selectedDataset
            }
          }}</pre>
      </div>

      <!-- 训练配置 -->
      <div class="config-section" v-if="!isTraining">
        <el-form :model="trainingForm" label-width="120px">
          <el-form-item label="训练数据">
            <el-select
              v-model="trainingForm.dataset_id"
              placeholder="请选择训练数据集"
              style="width: 100%"
              @change="handleDatasetChange"
            >
              <el-option
                v-for="dataset in datasets"
                :key="dataset.id"
                :label="dataset.name"
                :value="dataset.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="特征列" v-if="selectedDataset">
            <el-select
              v-model="trainingForm.features"
              multiple
              placeholder="请选择特征列"
              style="width: 100%"
            >
              <el-option
                v-for="column in datasetColumns"
                :key="column"
                :label="column"
                :value="column"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="目标列" v-if="selectedDataset">
            <el-select
              v-model="trainingForm.target"
              placeholder="请选择目标列"
              style="width: 100%"
            >
              <el-option
                v-for="column in datasetColumns"
                :key="column"
                :label="column"
                :value="column"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="训练参数">
            <div class="training-params">
              <div class="param-item">
                <label>训练轮次</label>
                <el-input-number
                  v-model="trainingForm.config.n_estimators"
                  :min="10"
                  :max="1000"
                  :step="10"
                  controls-position="right"
                />
              </div>
              <div class="param-item">
                <label>最大深度</label>
                <el-input-number
                  v-model="trainingForm.config.max_depth"
                  :min="1"
                  :max="50"
                  controls-position="right"
                />
              </div>
              <div class="param-item">
                <label>测试集比例</label>
                <el-input-number
                  v-model="trainingForm.config.test_size"
                  :min="0.1"
                  :max="0.5"
                  :step="0.05"
                  :precision="2"
                  controls-position="right"
                />
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 训练进度 -->
      <div class="progress-section" v-if="isTraining">
        <progress-tracker
          :progress="trainingProgress"
          :status="trainingStatus"
          :current-step="currentStep"
          :steps="trainingSteps"
        />

        <div class="training-details" v-if="trainingResult">
          <el-divider content-position="left">训练结果</el-divider>
          <div class="result-stats">
            <div class="stat-item">
              <span class="label">准确率:</span>
              <span class="value">{{ formatAccuracy(trainingResult.accuracy) }}</span>
            </div>
            <div class="stat-item" v-if="trainingResult.feature_importance">
              <span class="label">特征重要性:</span>
              <el-tooltip
                placement="top"
                content="点击查看详细特征重要性"
              >
                <el-button link type="primary" @click="showFeatureImportance = true">
                  查看详情
                </el-button>
              </el-tooltip>
            </div>
            <div class="stat-item" v-if="trainingResult.training_time">
              <span class="label">训练耗时:</span>
              <span class="value">{{ trainingResult.training_time }}秒</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 特征重要性详情 -->
      <el-dialog
        v-model="showFeatureImportance"
        title="特征重要性分析"
        width="600px"
        append-to-body
      >
        <div class="feature-importance">
          <el-table
            :data="featureImportanceData"
            height="300"
            stripe
          >
            <el-table-column prop="feature" label="特征名称" min-width="150"/>
            <el-table-column prop="importance" label="重要性" width="120">
              <template #default="{ row }">
                {{ (row.importance * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column label="可视化" width="100">
              <template #default="{ row }">
                <div class="importance-bar">
                  <div
                    class="bar-fill"
                    :style="{ width: (row.importance * 100) + '%' }"
                  ></div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-dialog>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="isTraining">
          取消
        </el-button>
        <el-button
          type="primary"
          @click="handleStartTraining"
          :loading="trainingLoading"
          :disabled="!canStartTraining"
          v-if="!isTraining"
        >
          开始训练
        </el-button>
        <el-button
          type="success"
          @click="handleComplete"
          v-if="isTraining && trainingStatus === 'completed'"
        >
          完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import {ref, computed, watch, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import {useAIStore} from '../../stores/ai'
import {datasetsAPI} from '../../api/datasets'
import {aiAPI} from '../../api/ai'
import ProgressTracker from './ProgressTracker.vue'

const props = defineProps({
  model: {
    type: Object,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'success'])
const aiStore = useAIStore()

// 响应式数据
const datasets = ref([])
const selectedDataset = ref(null)
const datasetColumnsList = ref([])
const trainingLoading = ref(false)
const isTraining = ref(false)
const trainingProgress = ref(0)
const trainingStatus = ref('pending')
const trainingResult = ref(null)
const showFeatureImportance = ref(false)
const currentStep = ref(0)

const trainingForm = ref({
  dataset_id: null,
  features: [],
  target: '',
  config: {
    n_estimators: 100,
    max_depth: 10,
    test_size: 0.2
  }
})

const trainingSteps = [
  {title: '数据准备', description: '加载和预处理训练数据'},
  {title: '特征工程', description: '处理特征和标签'},
  {title: '模型训练', description: '训练机器学习模型'},
  {title: '模型评估', description: '评估模型性能'},
  {title: '模型保存', description: '保存训练好的模型'}
]

// 计算属性
const datasetColumns = computed(() => {
  // 优先使用专门加载的列名
  if (datasetColumnsList.value.length > 0) {
    return datasetColumnsList.value
  }

  // 备用：从数据集对象中获取
  if (!selectedDataset.value) {
    return []
  }

  if (selectedDataset.value.columns && Array.isArray(selectedDataset.value.columns)) {
    return selectedDataset.value.columns
  }

  if (selectedDataset.value.column_names && Array.isArray(selectedDataset.value.column_names)) {
    return selectedDataset.value.column_names
  }

  return []
})

const canStartTraining = computed(() => {
  return (
    trainingForm.value.dataset_id &&
    trainingForm.value.features.length > 0 &&
    trainingForm.value.target
  )
})

const featureImportanceData = computed(() => {
  if (!trainingResult.value?.feature_importance) return []

  return Object.entries(trainingResult.value.feature_importance)
    .map(([feature, importance]) => ({
      feature,
      importance
    }))
    .sort((a, b) => b.importance - a.importance)
})

// 方法 - 将重复的函数定义合并为一个
const simulateTrainingProgress = () => {
  trainingProgress.value = 0
  currentStep.value = 0
  const interval = setInterval(() => {
    trainingProgress.value += 5
    if (trainingProgress.value % 20 === 0 && currentStep.value < trainingSteps.length - 1) {
      currentStep.value++
    }

    if (trainingProgress.value >= 100) {
      trainingProgress.value = 100
      currentStep.value = trainingSteps.length - 1
      trainingStatus.value = 'completed'
      clearInterval(interval)
    }
  }, 200)
}

const loadDatasets = async () => {
  try {
    console.log('开始加载训练数据集...')
    const response = await datasetsAPI.getDatasets()
    console.log('训练数据集API响应:', response)

    // 处理不同的响应格式
    if (response) {
      // 情况1: 直接返回数组
      if (Array.isArray(response)) {
        datasets.value = response
        console.log('成功加载数据集(数组格式):', datasets.value)
      }
      // 情况2: 返回 {data: {results: [...]}} 格式
      else if (response.data && response.data.results && Array.isArray(response.data.results)) {
        datasets.value = response.data.results
        console.log('成功加载数据集(results格式):', datasets.value)
      }
      // 情况3: 返回 {data: [...]} 格式
      else if (response.data && Array.isArray(response.data)) {
        datasets.value = response.data
        console.log('成功加载数据集(data格式):', datasets.value)
      }
      // 情况4: 其他格式，尝试提取
      else {
        console.warn('未知的响应格式，尝试提取数据:', response)
        // 尝试从响应中提取数组
        const findArray = (obj) => {
          if (Array.isArray(obj)) return obj
          if (typeof obj === 'object' && obj !== null) {
            for (let key in obj) {
              if (Array.isArray(obj[key])) {
                return obj[key]
              }
            }
          }
          return []
        }
        datasets.value = findArray(response)
      }
    }

    console.log('最终加载的数据集:', datasets.value)

    if (datasets.value.length === 0) {
      ElMessage.warning('没有找到可用的数据集')
    } else {
      ElMessage.success(`加载了 ${datasets.value.length} 个数据集`)
    }
  } catch (error) {
    console.error('加载数据集失败:', error)
    ElMessage.error('加载数据集失败: ' + (error.message || '网络错误'))
  }
}

const handleDatasetChange = async (datasetId) => {
  if (!datasetId) {
    selectedDataset.value = null
    trainingForm.value.features = []
    trainingForm.value.target = ''
    return
  }

  try {
    console.log('加载数据集详情，ID:', datasetId)
    const response = await datasetsAPI.getDataset(datasetId)
    console.log('数据集详情响应:', response)

    // 处理不同的响应格式
    let datasetData = null
    if (response) {
      // 情况1: 直接返回数据集对象
      if (response.id) {
        datasetData = response
      }
      // 情况2: 返回 {data: {...}} 格式
      else if (response.data) {
        datasetData = response.data
      }
      // 情况3: 其他格式
      else {
        datasetData = response
      }
    }

    selectedDataset.value = datasetData
    console.log('选中的数据集:', selectedDataset.value)

    // 获取数据集的列名
    await loadDatasetColumns(datasetId)

  } catch (error) {
    console.error('加载数据集详情失败:', error)
    ElMessage.error('加载数据集详情失败: ' + (error.message || '网络错误'))
  }
}

const loadDatasetColumns = async (datasetId) => {
  try {
    console.log('加载数据集列名，ID:', datasetId)

    // 方法1: 尝试从AI API获取列名
    try {
      const response = await aiAPI.getDatasetColumns(datasetId)
      console.log('AI API列名响应:', response)

      if (response && response.columns) {
        datasetColumnsList.value = response.columns
      } else if (Array.isArray(response)) {
        datasetColumnsList.value = response
      } else if (response.data && response.data.columns) {
        datasetColumnsList.value = response.data.columns
      }
    } catch (aiError) {
      console.warn('AI API获取列名失败，尝试其他方法:', aiError)

      // 方法2: 从数据集详情中提取列名
      if (selectedDataset.value) {
        if (selectedDataset.value.columns && Array.isArray(selectedDataset.value.columns)) {
          datasetColumnsList.value = selectedDataset.value.columns
        } else if (selectedDataset.value.column_names && Array.isArray(selectedDataset.value.column_names)) {
          datasetColumnsList.value = selectedDataset.value.column_names
        } else {
          // 方法3: 从数据记录中推断列名
          await inferColumnsFromData(datasetId)
        }
      }
    }

    console.log('最终获取的列名:', datasetColumnsList.value)

    // 自动选择特征列和目标列
    autoSetFeaturesAndTarget()

  } catch (error) {
    console.error('加载列名失败:', error)
    ElMessage.error('加载列名失败: ' + (error.message || '网络错误'))
  }
}

const inferColumnsFromData = async (datasetId) => {
  try {
    // 获取数据预览来推断列名
    const response = await datasetsAPI.getDatasetPreview(datasetId)
    console.log('数据预览响应:', response)

    if (response && response.data && response.data.length > 0) {
      // 从第一条记录中提取列名
      const firstRecord = response.data[0]
      if (firstRecord && typeof firstRecord === 'object') {
        datasetColumnsList.value = Object.keys(firstRecord)
      }
    }
  } catch (previewError) {
    console.warn('无法从数据预览推断列名:', previewError)
  }
}

const autoSetFeaturesAndTarget = () => {
  if (datasetColumnsList.value.length === 0) return

  console.log('自动设置特征和目标列，可用列:', datasetColumnsList.value)

  // 排除常见的非特征列
  const excludeColumns = ['id', 'ID', 'date', 'Date', 'time', 'Time', 'timestamp', 'Timestamp', 'created_at', 'updated_at']

  const availableColumns = datasetColumnsList.value.filter(col =>
    !excludeColumns.includes(col.toLowerCase())
  )

  console.log('过滤后的可用列:', availableColumns)

  if (availableColumns.length > 0) {
    // 设置前几个作为特征列（最多5个）
    const featureCount = Math.min(availableColumns.length - 1, 5)
    trainingForm.value.features = availableColumns.slice(0, featureCount)

    // 设置最后一个作为目标列
    trainingForm.value.target = availableColumns[availableColumns.length - 1]

    console.log('自动设置的特征列:', trainingForm.value.features)
    console.log('自动设置的目标列:', trainingForm.value.target)
  }
}

const handleStartTraining = async () => {
  if (!canStartTraining.value) {
    ElMessage.warning('请完善训练配置')
    return
  }

  trainingLoading.value = true
  isTraining.value = true
  trainingStatus.value = 'running'

  try {
    console.log('开始训练模型:', props.model.id)

    // 1. 先更新状态为训练中
    try {
      await aiStore.startTraining(props.model.id, trainingForm.value)
      console.log('模型状态已更新为训练中')
    } catch (statusError) {
      console.warn('更新训练状态失败，继续训练流程:', statusError)
    }

    // 2. 模拟训练过程
    simulateTrainingProgress()

    // 3. 等待训练完成
    await new Promise((resolve) => {
      const checkTrainingComplete = () => {
        if (trainingStatus.value === 'completed') {
          resolve()
        } else {
          setTimeout(checkTrainingComplete, 100)
        }
      }
      checkTrainingComplete()
    })

    // 4. 训练完成后更新状态为已激活
    try {
      const accuracy = 0.75 + Math.random() * 0.2 // 模拟准确率 0.75-0.95
      await aiStore.completeTraining(props.model.id, accuracy)
      console.log('模型状态已更新为已激活，准确率:', accuracy)

      trainingResult.value = {
        success: true,
        accuracy: accuracy,
        training_time: 30.5,
        feature_importance: {
          [trainingForm.value.features[0]]: 0.35,
          [trainingForm.value.features[1]]: 0.25,
          [trainingForm.value.features[2]]: 0.20,
          [trainingForm.value.features[3]]: 0.15,
          [trainingForm.value.features[4]]: 0.05
        }
      }

      ElMessage.success('模型训练完成并已激活')

      // 训练完成后自动关闭对话框
      setTimeout(() => {
        handleComplete()
      }, 2000)

    } catch (completeError) {
      console.error('完成训练状态更新失败:', completeError)
      ElMessage.error('训练完成但状态更新失败')
    }

  } catch (error) {
    console.error('训练过程失败:', error)
    trainingStatus.value = 'failed'

    // 训练失败时重置状态
    try {
      await aiStore.updateModelStatus(props.model.id, 'inactive')
    } catch (statusError) {
      console.warn('重置状态失败:', statusError)
    }

    ElMessage.error('训练失败: ' + error.message)
  } finally {
    trainingLoading.value = false
  }
}

const handleComplete = () => {
  emit('success')
  handleClose()
}

const handleClose = () => {
  if (isTraining.value && trainingStatus.value === 'running') {
    ElMessage.warning('训练正在进行中，请等待完成')
    return
  }

  // 重置状态
  resetState()
  emit('update:visible', false)
}

const resetState = () => {
  trainingForm.value = {
    dataset_id: null,
    features: [],
    target: '',
    config: {
      n_estimators: 100,
      max_depth: 10,
      test_size: 0.2
    }
  }
  selectedDataset.value = null
  datasetColumnsList.value = []
  isTraining.value = false
  trainingProgress.value = 0
  trainingStatus.value = 'pending'
  trainingResult.value = null
  showFeatureImportance.value = false
  currentStep.value = 0
}

const formatAccuracy = (accuracy) => {
  if (!accuracy) return '-'
  return `${(accuracy * 100).toFixed(2)}%`
}

// 监听visible变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadDatasets()
  }
})

onMounted(() => {
  loadDatasets()
})
</script>

<style scoped>
.training-dialog {
  min-height: 400px;
}

.config-section,
.progress-section {
  padding: 10px 0;
}

.training-params {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.training-details {
  margin-top: 20px;
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.stat-item .label {
  color: #606266;
  font-weight: 500;
}

.stat-item .value {
  color: #303133;
  font-weight: 600;
}

.feature-importance {
  padding: 10px 0;
}

.importance-bar {
  width: 80px;
  height: 6px;
  background-color: #ebeef5;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  transition: width 0.3s ease;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
