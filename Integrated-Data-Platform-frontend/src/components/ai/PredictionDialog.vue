<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/ai/PredictionDialog.vue-->
<template>
  <el-dialog
    :model-value="visible"
    :title="`使用模型预测 - ${model?.name}`"
    width="900px"
    :before-close="handleClose"
    @update:model-value="$emit('update:visible', $event)"
  >
    <!-- 添加调试信息 -->
    <div v-if="true"
         style="background: #f5f5f5; padding: 10px; margin-bottom: 20px; border-radius: 4px;">
      <h4>预测对话框调试信息:</h4>
      <pre>{{
          {
            datasetsCount: datasets.length,
            datasets: datasets.map(d => ({id: d.id, name: d.name})),
            selectedDatasetId: predictionForm.dataset_id,
            selectedDataset: selectedDataset,
            currentStep: currentStep,
            dataSourceType: predictionForm.data_source_type
          }
        }}</pre>
    </div>
    <!-- 对话框内容保持不变 -->
    <div class="prediction-dialog">
      <el-steps :active="currentStep" align-center class="prediction-steps">
        <el-step title="选择数据" description="选择预测数据源"/>
        <el-step title="配置参数" description="设置预测参数"/>
        <el-step title="执行预测" description="运行预测任务"/>
        <el-step title="查看结果" description="分析预测结果"/>
      </el-steps>

      <div class="step-content">
        <!-- 步骤1: 选择数据 -->
        <div v-if="currentStep === 0" class="step-panel">
          <el-form :model="predictionForm" label-width="100px">
            <el-form-item label="数据源类型">
              <el-radio-group v-model="predictionForm.data_source_type">
                <el-radio label="dataset">现有数据集</el-radio>
                <el-radio label="upload">上传文件</el-radio>
                <el-radio label="manual">手动输入</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="选择数据集" v-if="predictionForm.data_source_type === 'dataset'">
              <el-select
                v-model="predictionForm.dataset_id"
                placeholder="请选择数据集"
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

            <el-form-item label="上传文件" v-if="predictionForm.data_source_type === 'upload'">
              <el-upload
                class="upload-demo"
                drag
                action="#"
                :auto-upload="false"
                :on-change="handleFileUpload"
                :file-list="fileList"
                accept=".csv,.xlsx,.xls"
              >
                <el-icon class="el-icon--upload">
                  <upload-filled/>
                </el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 csv、xlsx 格式文件，文件大小不超过 10MB
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item label="手动输入" v-if="predictionForm.data_source_type === 'manual'">
              <div class="manual-input">
                <el-button @click="addSampleData" type="primary" size="small">
                  添加样本数据
                </el-button>
                <el-table
                  :data="manualData"
                  style="width: 100%; margin-top: 10px"
                  border
                >
                  <el-table-column
                    v-for="column in inputColumns"
                    :key="column"
                    :prop="column"
                    :label="column"
                  >
                    <template #default="{ row, $index }">
                      <el-input
                        v-model="row[column]"
                        size="small"
                        @change="handleManualDataChange"
                      />
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="80">
                    <template #default="{ $index }">
                      <el-button
                        link
                        type="danger"
                        size="small"
                        @click="removeManualData($index)"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤2: 配置参数 -->
        <div v-if="currentStep === 1" class="step-panel">
          <el-alert
            title="预测参数配置"
            description="根据模型要求配置预测参数"
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          />

          <el-form :model="predictionForm" label-width="120px">
            <el-form-item label="预测数量">
              <el-input-number
                v-model="predictionForm.prediction_count"
                :min="1"
                :max="1000"
                controls-position="right"
              />
              <span class="param-tip">设置需要预测的数据条数</span>
            </el-form-item>

            <el-form-item label="置信阈值">
              <el-slider
                v-model="predictionForm.confidence_threshold"
                :min="0.5"
                :max="1"
                :step="0.05"
                show-stops
              />
              <span class="param-tip">{{
                  (predictionForm.confidence_threshold * 100).toFixed(0)
                }}%</span>
            </el-form-item>

            <el-form-item label="输出格式">
              <el-radio-group v-model="predictionForm.output_format">
                <el-radio label="json">JSON格式</el-radio>
                <el-radio label="csv">CSV文件</el-radio>
                <el-radio label="excel">Excel文件</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="包含置信度" v-if="model?.model_type !== 'classification'">
              <el-switch v-model="predictionForm.include_confidence"/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤3: 执行预测 -->
        <div v-if="currentStep === 2" class="step-panel">
          <div class="execution-panel">
            <progress-tracker
              :progress="predictionProgress"
              :status="predictionStatus"
              :current-step="executionStep"
              :steps="executionSteps"
            />

            <div class="execution-info" v-if="predictionResult">
              <el-divider content-position="left">预测信息</el-divider>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">处理数据:</span>
                  <span class="value">{{ predictionResult.processed_count }} 条</span>
                </div>
                <div class="info-item">
                  <span class="label">预测耗时:</span>
                  <span class="value">{{ predictionResult.execution_time }} 秒</span>
                </div>
                <div class="info-item">
                  <span class="label">平均置信度:</span>
                  <span class="value">{{
                      (predictionResult.average_confidence * 100).toFixed(1)
                    }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤4: 查看结果 -->
        <div v-if="currentStep === 3" class="step-panel">
          <div class="results-panel">
            <div class="results-header">
              <h3>预测结果</h3>
              <div class="result-actions">
                <el-button @click="exportResults" type="primary">
                  <el-icon>
                    <Download/>
                  </el-icon>
                  导出结果
                </el-button>
                <el-button @click="saveToDataset">
                  <el-icon>
                    <FolderAdd/>
                  </el-icon>
                  保存为数据集
                </el-button>
              </div>
            </div>

            <el-table
              :data="predictionResults"
              border
              stripe
              style="width: 100%"
              max-height="400"
            >
              <el-table-column
                v-for="column in resultColumns"
                :key="column"
                :prop="column"
                :label="column"
                min-width="120"
              />
              <el-table-column
                prop="prediction"
                label="预测值"
                width="120"
              />
              <el-table-column
                v-if="predictionForm.include_confidence"
                prop="confidence"
                label="置信度"
                width="100"
              >
                <template #default="{ row }">
                  <el-tag :type="getConfidenceTag(row.confidence)">
                    {{ (row.confidence * 100).toFixed(1) }}%
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <div class="results-summary" v-if="predictionResult">
              <el-divider content-position="left">预测摘要</el-divider>
              <div class="summary-stats">
                <el-statistic title="总预测数" :value="predictionResult.processed_count"/>
                <el-statistic title="平均置信度"
                              :value="(predictionResult.average_confidence * 100).toFixed(1)"
                              suffix="%"/>
                <el-statistic title="高置信度" :value="predictionResult.high_confidence_count"/>
                <el-statistic title="执行时间" :value="predictionResult.execution_time"
                              suffix="秒"/>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handlePrevStep" :disabled="currentStep === 0">
          上一步
        </el-button>
        <el-button
          v-if="currentStep < 3"
          type="primary"
          @click="handleNextStep"
          :loading="predictionLoading"
          :disabled="!canProceed"
        >
          {{ currentStep === 2 ? '开始预测' : '下一步' }}
        </el-button>
        <el-button
          v-if="currentStep === 3"
          type="success"
          @click="handleComplete"
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
import {UploadFilled, Download, FolderAdd} from '@element-plus/icons-vue'
import {useAIStore} from '../../stores/ai'
import {datasetsAPI} from '../../api/datasets'
import ProgressTracker from './ProgressTracker.vue'

// 定义 props 和 emits
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
const currentStep = ref(0)
const datasets = ref([])
const selectedDataset = ref(null)
const fileList = ref([])
const manualData = ref([])
const predictionLoading = ref(false)
const predictionProgress = ref(0)
const predictionStatus = ref('pending')
const predictionResult = ref(null)
const executionStep = ref(0)

const predictionForm = ref({
  data_source_type: 'dataset',
  dataset_id: null,
  prediction_count: 10,
  confidence_threshold: 0.8,
  output_format: 'json',
  include_confidence: true
})

const executionSteps = [
  {title: '数据加载', description: '加载预测数据'},
  {title: '数据预处理', description: '清洗和转换数据'},
  {title: '模型推理', description: '执行预测计算'},
  {title: '结果处理', description: '生成预测结果'},
  {title: '输出生成', description: '创建输出文件'}
]

// 计算属性
const inputColumns = computed(() => {
  if (!props.model?.feature_columns) return []
  return props.model.feature_columns
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return predictionForm.value.data_source_type === 'manual' ?
        manualData.value.length > 0 :
        predictionForm.value.dataset_id || fileList.value.length > 0
    case 1:
      return true
    case 2:
      return true
    default:
      return true
  }
})

const predictionResults = computed(() => {
  if (!predictionResult.value?.predictions) return []
  return predictionResult.value.predictions
})

const resultColumns = computed(() => {
  if (predictionResults.value.length === 0) return []
  return Object.keys(predictionResults.value[0]).filter(
    key => key !== 'prediction' && key !== 'confidence'
  )
})

// 方法
const loadDatasets = async () => {
  try {
    console.log('开始加载预测数据集...')
    const response = await datasetsAPI.getDatasets()
    console.log('预测数据集API响应:', response)

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

  } catch (error) {
    console.error('加载数据集详情失败:', error)
    ElMessage.error('加载数据集详情失败: ' + (error.message || '网络错误'))
  }
}

const handlePredict = () => {
  if (!canPredict.value) {
    const status = props.model.status || 'inactive'
    if (status === 'training') {
      ElMessage.warning('模型正在训练中，请等待训练完成')
    } else if (status === 'inactive') {
      ElMessage.warning('模型未激活，请先训练模型')
    } else if (status === 'error') {
      ElMessage.error('模型出现错误，无法进行预测')
    }
    return
  }
  emit('predict', props.model)
}

const handleFileUpload = (file) => {
  // 这里可以添加文件验证逻辑
  console.log('上传文件:', file)
  fileList.value = [file]
}

const addSampleData = () => {
  const sampleRow = {}
  inputColumns.value.forEach(column => {
    sampleRow[column] = ''
  })
  manualData.value.push(sampleRow)
}

const removeManualData = (index) => {
  manualData.value.splice(index, 1)
}

const handleManualDataChange = () => {
  // 手动数据变化处理
  console.log('手动数据更新:', manualData.value)
}

const simulatePredictionProgress = () => {
  predictionProgress.value = 0
  executionStep.value = 0
  const interval = setInterval(() => {
    predictionProgress.value += 4
    if (predictionProgress.value % 20 === 0 && executionStep.value < executionSteps.length - 1) {
      executionStep.value++
    }

    if (predictionProgress.value >= 100) {
      predictionProgress.value = 100
      executionStep.value = executionSteps.length - 1
      predictionStatus.value = 'completed'

      // 生成模拟结果
      generateMockResults()
      clearInterval(interval)
    }
  }, 150)
}

const generateMockResults = () => {
  const results = []
  const count = predictionForm.value.prediction_count

  for (let i = 0; i < count; i++) {
    const row = {}
    inputColumns.value.forEach(column => {
      // 生成模拟数据
      if (column.includes('价格') || column.includes('金额')) {
        row[column] = (Math.random() * 100 + 10).toFixed(2)
      } else if (column.includes('数量')) {
        row[column] = Math.floor(Math.random() * 1000)
      } else {
        row[column] = `值${i + 1}`
      }
    })

    row.prediction = (Math.random() * 50 + 50).toFixed(2)
    if (predictionForm.value.include_confidence) {
      row.confidence = Math.random() * 0.3 + 0.7 // 0.7-1.0之间的置信度
    }

    results.push(row)
  }

  predictionResult.value = {
    processed_count: count,
    execution_time: (Math.random() * 5 + 1).toFixed(2),
    average_confidence: 0.85,
    high_confidence_count: Math.floor(count * 0.8),
    predictions: results
  }
}

const handleNextStep = async () => {
  if (currentStep.value === 2) {
    // 开始预测
    predictionLoading.value = true
    predictionStatus.value = 'running'

    try {
      simulatePredictionProgress()

      // 实际调用API
      // const inputData = prepareInputData()
      // const result = await aiStore.predict(props.model.id, inputData)
      // predictionResult.value = result

      ElMessage.success('预测完成')
      currentStep.value++
    } catch (error) {
      predictionStatus.value = 'failed'
      ElMessage.error('预测失败: ' + error.message)
    } finally {
      predictionLoading.value = false
    }
  } else {
    currentStep.value++
  }
}

const handlePrevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const handleComplete = () => {
  emit('success')
  handleClose()
}

const handleClose = () => {
  if (predictionStatus.value === 'running') {
    ElMessage.warning('预测正在进行中，请等待完成')
    return
  }

  resetState()
  emit('update:visible', false)
}

const resetState = () => {
  currentStep.value = 0
  predictionForm.value = {
    data_source_type: 'dataset',
    dataset_id: null,
    prediction_count: 10,
    confidence_threshold: 0.8,
    output_format: 'json',
    include_confidence: true
  }
  selectedDataset.value = null
  fileList.value = []
  manualData.value = []
  predictionLoading.value = false
  predictionProgress.value = 0
  predictionStatus.value = 'pending'
  predictionResult.value = null
  executionStep.value = 0
}

const getConfidenceTag = (confidence) => {
  if (confidence >= 0.9) return 'success'
  if (confidence >= 0.7) return 'warning'
  return 'danger'
}

const exportResults = () => {
  ElMessage.info('导出功能开发中')
}

const saveToDataset = () => {
  ElMessage.info('保存数据集功能开发中')
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
.prediction-dialog {
  min-height: 500px;
}

.prediction-steps {
  margin-bottom: 30px;
}

.step-content {
  min-height: 300px;
}

.step-panel {
  padding: 10px 0;
}

.upload-demo {
  width: 100%;
}

.manual-input {
  width: 100%;
}

.param-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.execution-panel {
  padding: 20px 0;
}

.execution-info {
  margin-top: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.info-item .label {
  color: #606266;
  font-weight: 500;
}

.info-item .value {
  color: #303133;
  font-weight: 600;
}

.results-panel {
  padding: 10px 0;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-header h3 {
  margin: 0;
  color: #303133;
}

.result-actions {
  display: flex;
  gap: 12px;
}

.results-summary {
  margin-top: 20px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
}
</style>
