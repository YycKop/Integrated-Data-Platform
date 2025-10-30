<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/components/ai/ModelForm.vue -->
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAIStore } from '../../stores/ai'
import { aiAPI } from '../../api/ai'

const props = defineProps({
  modelId: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['success', 'cancel'])

const aiStore = useAIStore()

// 响应式数据
const formRef = ref()
const loading = ref(false)
const datasets = ref([])
const datasetsLoading = ref(false)
const columnsLoading = ref(false)
const selectedDataset = ref(null)
const datasetColumns = ref([])
const previewData = ref([])

const form = ref({
  name: '',
  model_type: '',
  description: '',
  training_data: null,
  features: [],
  target: '',
  config: {
    n_estimators: 100,
    max_depth: 10,
    test_size: 0.2
  }
})

const rules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  model_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ],
  training_data: [
    { required: true, message: '请选择训练数据', trigger: 'change' }
  ],
  features: [
    { required: true, message: '请选择特征列', trigger: 'change' }
  ],
  target: [
    { required: true, message: '请选择目标列', trigger: 'change' }
  ]
}

const modelTypes = [
  { value: 'price_prediction', label: '价格预测' },
  { value: 'yield_prediction', label: '产量预测' },
  { value: 'disease_detection', label: '病害检测' },
  { value: 'market_analysis', label: '市场分析' },
  { value: 'climate_impact', label: '气候影响分析' }
]

// 方法
const loadDatasets = async () => {
  datasetsLoading.value = true
  try {
    console.log('开始加载AI数据集...')
    const response = await aiAPI.getDatasets()
    console.log('AI数据集API完整响应:', response)

    // 修复：处理直接返回数组的情况
    if (response) {
      // 情况1: 直接返回数组（当前后端的行为）
      if (Array.isArray(response)) {
        datasets.value = response
        console.log('成功加载数据集(直接数组格式):', datasets.value)
        ElMessage.success(`加载了 ${datasets.value.length} 个数据集`)
      }
      // 情况2: 返回 {data: [...]} 格式
      else if (response.data && Array.isArray(response.data)) {
        datasets.value = response.data
        console.log('成功加载数据集(data数组格式):', datasets.value)
        ElMessage.success(`加载了 ${datasets.value.length} 个数据集`)
      }
      // 情况3: 返回 {success: true, data: [...]} 格式
      else if (response.success && Array.isArray(response.data)) {
        datasets.value = response.data
        console.log('成功加载数据集(success格式):', datasets.value)
        ElMessage.success(`加载了 ${datasets.value.length} 个数据集`)
      }
      // 情况4: 其他未知格式
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
        if (datasets.value.length > 0) {
          console.log('提取的数据集:', datasets.value)
          ElMessage.success(`加载了 ${datasets.value.length} 个数据集`)
        } else {
          console.error('无法解析API响应:', response)
          ElMessage.error('加载数据集失败: 无法解析响应格式')
        }
      }
    } else {
      console.error('API响应为空:', response)
      ElMessage.error('加载数据集失败: API响应为空')
    }
  } catch (error) {
    console.error('加载数据集失败:', error)
    ElMessage.error('加载数据集失败: ' + (error.message || '网络错误'))
  } finally {
    datasetsLoading.value = false
  }
}
const loadDatasetColumns = async (datasetId) => {
  if (!datasetId) {
    datasetColumns.value = []
    previewData.value = []
    return
  }

  columnsLoading.value = true
  try {
    console.log('加载数据集列名，ID:', datasetId)
    const response = await aiAPI.getDatasetColumns(datasetId)
    console.log('列名API完整响应:', response)

    // 修复：处理多种响应格式
    if (response) {
      let columns = []

      // 情况1: 直接返回 {columns: [...]} 格式
      if (response.columns && Array.isArray(response.columns)) {
        columns = response.columns
      }
      // 情况2: 直接返回数组
      else if (Array.isArray(response)) {
        columns = response
      }
      // 情况3: 返回 {data: {columns: [...]}} 格式
      else if (response.data && response.data.columns && Array.isArray(response.data.columns)) {
        columns = response.data.columns
      }
      // 情况4: 返回 {data: [...]} 格式
      else if (response.data && Array.isArray(response.data)) {
        columns = response.data
      }
      // 情况5: 其他格式，尝试提取
      else {
        console.warn('未知的列名响应格式，尝试提取:', response)
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
        columns = findArray(response)
      }

      if (columns.length > 0) {
        datasetColumns.value = columns
        console.log('成功加载列名:', datasetColumns.value)
        autoSetFeaturesAndTarget()
        await loadDatasetPreview(datasetId)
        ElMessage.success(`加载了 ${datasetColumns.value.length} 个列名`)
      } else {
        console.error('无法从响应中提取列名:', response)
        ElMessage.error('加载列名失败: 无法解析响应格式')
      }
    } else {
      console.error('列名API响应为空:', response)
      ElMessage.error('加载列名失败: API响应为空')
    }
  } catch (error) {
    console.error('加载列名失败:', error)
    ElMessage.error('加载列名失败: ' + (error.message || '网络错误'))
  } finally {
    columnsLoading.value = false
  }
}
const loadDatasetPreview = async (datasetId) => {
  try {
    console.log('加载数据预览，ID:', datasetId)
    const response = await aiAPI.getDatasetPreview(datasetId)
    console.log('预览API完整响应:', response)

    // 修复：处理多种响应格式
    if (response) {
      let previewDataArray = []

      // 情况1: 直接返回 {data: [...]} 格式
      if (response.data && Array.isArray(response.data)) {
        previewDataArray = response.data
      }
      // 情况2: 直接返回数组
      else if (Array.isArray(response)) {
        previewDataArray = response
      }
      // 情况3: 返回 {success: true, data: [...]} 格式
      else if (response.success && Array.isArray(response.data)) {
        previewDataArray = response.data
      }
      // 情况4: 其他格式，尝试提取
      else {
        console.warn('未知的预览响应格式，尝试提取:', response)
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
        previewDataArray = findArray(response)
      }

      if (previewDataArray.length > 0) {
        previewData.value = previewDataArray
        console.log('成功加载预览数据:', previewData.value)
      } else {
        console.warn('预览数据为空或格式错误:', response)
      }
    } else {
      console.warn('预览API响应为空:', response)
    }
  } catch (error) {
    console.warn('加载数据预览失败:', error)
    // 预览失败不影响主要功能
  }
}
const autoSetFeaturesAndTarget = () => {
  if (datasetColumns.value.length === 0) return

  console.log('自动设置特征和目标列，可用列:', datasetColumns.value)

  // 排除常见的非特征列
  const excludeColumns = ['id', 'ID', 'date', 'Date', 'time', 'Time', 'timestamp', 'Timestamp', 'created_at', 'updated_at']

  const availableColumns = datasetColumns.value.filter(col =>
    !excludeColumns.includes(col.toLowerCase())
  )

  console.log('过滤后的可用列:', availableColumns)

  if (availableColumns.length > 0) {
    // 设置前几个作为特征列（最多5个）
    const featureCount = Math.min(availableColumns.length - 1, 5)
    form.value.features = availableColumns.slice(0, featureCount)

    // 设置最后一个作为目标列
    form.value.target = availableColumns[availableColumns.length - 1]

    console.log('自动设置的特征列:', form.value.features)
    console.log('自动设置的目标列:', form.value.target)
  }
}

const handleDatasetChange = async (datasetId) => {
  console.log('选择的数据集ID:', datasetId)

  if (!datasetId) {
    selectedDataset.value = null
    datasetColumns.value = []
    previewData.value = []
    form.value.features = []
    form.value.target = ''
    return
  }

  // 找到选中的数据集信息
  selectedDataset.value = datasets.value.find(d => d.id === datasetId) || null
  console.log('选中的数据集:', selectedDataset.value)

  // 加载该数据集的列名
  await loadDatasetColumns(datasetId)
}

const handleModelTypeChange = (type) => {
  console.log('选择模型类型:', type)
  // 根据模型类型设置默认配置
  const defaultConfigs = {
    price_prediction: { n_estimators: 100, max_depth: 10 },
    yield_prediction: { n_estimators: 150, max_depth: 15 },
    disease_detection: { n_estimators: 200, max_depth: 20 }
  }

  if (defaultConfigs[type]) {
    form.value.config = { ...form.value.config, ...defaultConfigs[type] }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const loadFullPreview = () => {
  ElMessage.info('完整数据预览功能开发中...')
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    // 准备提交数据
    const submitData = {
      name: form.value.name,
      model_type: form.value.model_type,
      description: form.value.description,
      training_data: form.value.training_data,
      feature_columns: form.value.features,
      target_column: form.value.target,
      training_config: form.value.config
    }

    console.log('提交的模型数据:', submitData)

    try {
      if (props.modelId) {
        await aiStore.updateModel(props.modelId, submitData)
        ElMessage.success('模型更新成功')
      } else {
        await aiStore.createModel(submitData)
        ElMessage.success('模型创建成功')
      }

      // 修复：确保成功后再触发事件
      emit('success')
    } catch (error) {
      console.error('模型操作失败:', error)
      ElMessage.error('操作失败: ' + (error.message || '未知错误'))
      // 不触发success事件，因为操作失败了
    }
  } catch (error) {
    console.error('表单验证失败:', error)
    ElMessage.error('请检查表单数据')
  } finally {
    loading.value = false
  }
}

const loadModelDetail = async () => {
  if (!props.modelId) return

  try {
    console.log('开始加载模型详情，ID:', props.modelId)
    const response = await aiAPI.getModel(props.modelId)
    console.log('模型详情API响应:', response)

    // 处理不同的响应格式
    let modelData = null
    if (response) {
      // 情况1: 直接返回模型对象
      if (response.id) {
        modelData = response
      }
      // 情况2: 返回 {data: {...}} 格式
      else if (response.data) {
        modelData = response.data
      }
      // 情况3: 其他格式
      else {
        modelData = response
      }
    }

    if (modelData) {
      form.value = {
        name: modelData.name,
        model_type: modelData.model_type,
        description: modelData.description,
        training_data: modelData.training_data,
        features: modelData.feature_columns || [],
        target: modelData.target_column || '',
        config: modelData.training_config || {
          n_estimators: 100,
          max_depth: 10,
          test_size: 0.2
        }
      }

      console.log('加载的模型详情表单数据:', form.value)

      // 如果模型有训练数据，加载对应的数据集信息
      if (modelData.training_data) {
        await loadDatasets() // 确保数据集列表已加载
        // 等待数据集加载完成后再设置选中的数据集
        setTimeout(() => {
          selectedDataset.value = datasets.value.find(d => d.id === modelData.training_data) || null
          if (selectedDataset.value) {
            loadDatasetColumns(modelData.training_data)
          }
        }, 100)
      }
    } else {
      console.error('无法解析模型详情数据:', response)
      ElMessage.error('加载模型详情失败: 数据格式错误')
    }
  } catch (error) {
    console.error('加载模型详情失败:', error)
    ElMessage.error('加载模型详情失败: ' + (error.message || '未知错误'))
  }
}

// 生命周期
onMounted(() => {
  console.log('ModelForm组件挂载')
  loadDatasets()
  if (props.modelId) {
    loadModelDetail()
  }
})

// 添加调试信息到模板中
// 在模板中添加更详细的调试信息
const debugInfo = computed(() => {
  return {
    datasetsCount: datasets.value.length,
    datasets: datasets.value.map(d => ({ id: d.id, name: d.name })),
    selectedDataset: selectedDataset.value,
    columnsCount: datasetColumns.value.length,
    columns: datasetColumns.value,
    features: form.value.features,
    target: form.value.target,
    formTrainingData: form.value.training_data
  }
})
</script>

<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
    label-position="right"
  >
    <!-- 调试信息（开发时显示） -->
    <div v-if="true" style="background: #f5f5f5; padding: 10px; margin-bottom: 20px; border-radius: 4px;">
      <h4>调试信息:</h4>
      <pre>{{ debugInfo }}</pre>
    </div>

    <el-form-item label="模型名称" prop="name">
      <el-input
        v-model="form.name"
        placeholder="请输入模型名称"
        maxlength="50"
        show-word-limit
      />
    </el-form-item>

    <el-form-item label="模型类型" prop="model_type">
      <el-select
        v-model="form.model_type"
        placeholder="请选择模型类型"
        style="width: 100%"
        @change="handleModelTypeChange"
      >
        <el-option
          v-for="type in modelTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="训练数据" prop="training_data">
      <el-select
        v-model="form.training_data"
        placeholder="请选择训练数据集"
        style="width: 100%"
        filterable
        @change="handleDatasetChange"
        :loading="datasetsLoading"
      >
        <el-option
          v-for="dataset in datasets"
          :key="dataset.id"
          :label="dataset.name"
          :value="dataset.id"
        />
      </el-select>
      <div v-if="selectedDataset" class="dataset-info">
        <small>记录数: {{ selectedDataset.record_count || 0 }} | 创建时间: {{ formatDate(selectedDataset.created_at) }}</small>
      </div>
      <div v-else-if="datasetsLoading" class="dataset-info">
        <small>加载中...</small>
      </div>
      <div v-else-if="datasets.length === 0" class="dataset-info">
        <small>没有可用的数据集</small>
      </div>
    </el-form-item>

    <el-form-item label="模型描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入模型描述"
        maxlength="200"
        show-word-limit
      />
    </el-form-item>

    <el-form-item label="特征列" prop="features">
      <el-select
        v-model="form.features"
        multiple
        placeholder="请选择特征列"
        style="width: 100%"
        :disabled="!selectedDataset || columnsLoading"
        :loading="columnsLoading"
      >
        <el-option
          v-for="column in datasetColumns"
          :key="column"
          :label="column"
          :value="column"
        />
      </el-select>
      <div class="help-text">
        <small>选择用于训练模型的特征变量</small>
      </div>
    </el-form-item>

    <el-form-item label="目标列" prop="target">
      <el-select
        v-model="form.target"
        placeholder="请选择目标列"
        style="width: 100%"
        :disabled="!selectedDataset || columnsLoading"
        :loading="columnsLoading"
      >
        <el-option
          v-for="column in datasetColumns"
          :key="column"
          :label="column"
          :value="column"
        />
      </el-select>
      <div class="help-text">
        <small>选择要预测的目标变量</small>
      </div>
    </el-form-item>

    <el-form-item label="训练配置">
      <div class="config-grid">
        <div class="config-item">
          <label>训练轮次</label>
          <el-input-number
            v-model="form.config.n_estimators"
            :min="10"
            :max="1000"
            :step="10"
            controls-position="right"
          />
        </div>
        <div class="config-item">
          <label>最大深度</label>
          <el-input-number
            v-model="form.config.max_depth"
            :min="1"
            :max="50"
            controls-position="right"
          />
        </div>
        <div class="config-item">
          <label>测试集比例</label>
          <el-input-number
            v-model="form.config.test_size"
            :min="0.1"
            :max="0.5"
            :step="0.05"
            :precision="2"
            controls-position="right"
          />
        </div>
      </div>
    </el-form-item>

    <!-- 数据集预览 -->
    <el-form-item v-if="previewData.length > 0" label="数据预览">
      <div class="preview-table">
        <el-table :data="previewData" height="200" border size="small">
          <el-table-column
            v-for="column in datasetColumns.slice(0, 6)"
            :key="column"
            :prop="column"
            :label="column"
            min-width="120"
          >
            <template #default="{ row }">
              {{ row[column] }}
            </template>
          </el-table-column>
          <el-table-column v-if="datasetColumns.length > 6" label="...">
            <template #default>
              <span class="text-muted">...</span>
            </template>
          </el-table-column>
        </el-table>
        <div class="preview-info">
          <small>显示前{{ previewData.length }}条记录，共 {{ datasetColumns.length }} 列</small>
          <el-button type="text" size="small" @click="loadFullPreview">查看完整数据</el-button>
        </div>
      </div>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        {{ modelId ? '更新模型' : '创建模型' }}
      </el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<style scoped>
.config-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.dataset-info {
  margin-top: 4px;
}

.help-text {
  margin-top: 4px;
}

.preview-table {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
}

.preview-info {
  padding: 8px;
  background: #f5f7fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-muted {
  color: #909399;
}
</style>
