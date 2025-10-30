<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/components/ai/AnalysisPanel.vue -->
<template>
  <div class="analysis-panel">
    <el-card class="panel-card">
      <template #header>
        <div class="card-header">
          <span>分析配置</span>
          <el-button
            type="text"
            @click="$emit('refresh-datasets')"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-form :model="analysisForm" :rules="rules" ref="formRef" label-width="80px">
        <!-- 数据集选择 -->
        <el-form-item label="数据集" prop="dataset">
          <el-select
            v-model="analysisForm.dataset"
            placeholder="请选择要分析的数据集"
            style="width: 100%"
            :loading="loading"
            @change="handleDatasetChange"
          >
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id"
            >
              <div class="dataset-option">
                <span class="dataset-name">{{ dataset.name }}</span>
                <span class="dataset-info">
                  {{ dataset.record_count || 0 }} 条记录 •
                  {{ formatDate(dataset.created_at) }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 分析类型选择 -->
        <el-form-item label="分析类型" prop="type">
          <el-select
            v-model="analysisForm.type"
            placeholder="请选择分析类型"
            style="width: 100%"
            @change="handleTypeChange"
          >
            <el-option label="市场趋势分析" value="market_trends" />
            <el-option label="价格预测分析" value="price_prediction" />
            <el-option label="产量预测分析" value="yield_prediction" />
            <el-option label="病害检测分析" value="disease_detection" />
            <el-option label="市场分析洞察" value="market_analysis" />
          </el-select>
        </el-form-item>

        <!-- 动态参数配置 -->
        <div v-if="analysisForm.type" class="analysis-params">
          <el-divider content-position="left">分析参数</el-divider>

          <!-- 市场趋势分析参数 -->
          <div v-if="analysisForm.type === 'market_trends'">
            <el-form-item label="时间字段">
              <el-select v-model="analysisForm.params.timeField" placeholder="选择时间字段" style="width: 100%">
                <el-option
                  v-for="column in datasetColumns"
                  :key="column"
                  :label="column"
                  :value="column"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="价格字段">
              <el-select v-model="analysisForm.params.priceField" placeholder="选择价格字段" style="width: 100%">
                <el-option
                  v-for="column in datasetColumns"
                  :key="column"
                  :label="column"
                  :value="column"
                />
              </el-select>
            </el-form-item>
          </div>

          <!-- 价格预测参数 -->
          <div v-if="analysisForm.type === 'price_prediction'">
            <el-form-item label="特征字段">
              <el-select
                v-model="analysisForm.params.features"
                multiple
                placeholder="选择特征字段"
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

            <el-form-item label="目标字段">
              <el-select v-model="analysisForm.params.target" placeholder="选择目标字段" style="width: 100%">
                <el-option
                  v-for="column in datasetColumns"
                  :key="column"
                  :label="column"
                  :value="column"
                />
              </el-select>
            </el-form-item>
          </div>

          <!-- 通用参数 -->
          <el-form-item label="分析描述">
            <el-input
              v-model="analysisForm.params.description"
              type="textarea"
              :rows="3"
              placeholder="请输入分析目标或特殊要求..."
            />
          </el-form-item>
        </div>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="analyzing"
            :disabled="!analysisForm.dataset || !analysisForm.type"
            @click="handleAnalyze"
          >
            <template #icon>
              <el-icon><Search /></el-icon>
            </template>
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据集信息卡片 -->
    <el-card v-if="selectedDataset" class="dataset-info-card">
      <template #header>
        <span>数据集信息</span>
      </template>

      <div class="dataset-details">
        <div class="detail-item">
          <label>数据集名称:</label>
          <span>{{ selectedDataset.name }}</span>
        </div>
        <div class="detail-item">
          <label>记录数量:</label>
          <span>{{ selectedDataset.record_count || 0 }} 条</span>
        </div>
        <div class="detail-item">
          <label>创建时间:</label>
          <span>{{ formatDate(selectedDataset.created_at) }}</span>
        </div>
        <div class="detail-item" v-if="selectedDataset.description">
          <label>描述:</label>
          <span class="dataset-description">{{ selectedDataset.description }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { aiAPI } from '../../api/ai'

// 定义 props 和 emits
const props = defineProps({
  datasets: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['analyze', 'refresh-datasets'])

// 响应式数据
const formRef = ref()
const analyzing = ref(false)
const datasetColumns = ref([])

const analysisForm = reactive({
  dataset: '',
  type: '',
  params: {
    timeField: '',
    priceField: '',
    features: [],
    target: '',
    description: ''
  }
})

const rules = {
  dataset: [
    { required: true, message: '请选择数据集', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择分析类型', trigger: 'change' }
  ]
}

// 计算属性
const selectedDataset = computed(() => {
  return props.datasets.find(d => d.id === analysisForm.dataset) || null
})

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const handleDatasetChange = async (datasetId) => {
  if (!datasetId) {
    datasetColumns.value = []
    return
  }

  try {
    console.log('开始获取数据集列名，数据集ID:', datasetId)
    const response = await aiAPI.getDatasetColumns(datasetId)
    console.log('列名获取结果:', response)

    if (response && response.columns) {
      datasetColumns.value = response.columns
    } else {
      datasetColumns.value = []
      ElMessage.warning('该数据集没有可用的列信息')
    }
  } catch (error) {
    console.error('获取数据集列名失败:', error)
    ElMessage.error('获取数据集列名失败')
    datasetColumns.value = []
  }
}

const handleTypeChange = (type) => {
  // 重置参数
  analysisForm.params = {
    timeField: '',
    priceField: '',
    features: [],
    target: '',
    description: ''
  }
}

const handleAnalyze = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    analyzing.value = true

    // 构建分析数据
    const analysisData = {
      dataset_id: analysisForm.dataset,
      type: analysisForm.type,
      data: {
        ...analysisForm.params,
        dataset_name: selectedDataset.value?.name
      }
    }

    console.log('发送分析请求:', analysisData)
    emit('analyze', analysisData)

  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    analyzing.value = false
  }
}

// 监听数据集变化
watch(() => props.datasets, (newDatasets) => {
  console.log('数据集列表更新:', newDatasets)
}, { immediate: true })
</script>

<style scoped>
.analysis-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-card {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dataset-option {
  display: flex;
  flex-direction: column;
}

.dataset-name {
  font-weight: 500;
}

.dataset-info {
  font-size: 12px;
  color: #909399;
}

.analysis-params {
  margin-top: 16px;
}

.dataset-info-card {
  margin-top: 16px;
}

.dataset-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.detail-item label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.dataset-description {
  color: #909399;
  font-size: 14px;
  text-align: right;
  max-width: 200px;
  word-break: break-word;
}
</style>
