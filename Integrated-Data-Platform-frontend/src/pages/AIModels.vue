<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/pages/AIModels.vue -->
<template>
  <div class="ai-models-page">
    <div class="page-header">
      <h1>AI模型管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon>
          <Plus/>
        </el-icon>
        新建模型
      </el-button>
    </div>

    <!-- 调试信息 -->
    <div v-if="false"
         style="background: #f5f5f5; padding: 10px; margin-bottom: 20px; border-radius: 4px;">
      <h4>模型状态调试信息:</h4>
      <pre>{{
          {
            modelsCount: models.length,
            models: models.map(m => ({
              id: m.id,
              name: m.name,
              status: m.status,
              statusText: getStatusText(m.status),
              accuracy: m.accuracy
            }))
          }
        }}</pre>
    </div>

    <div class="model-stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <stat-card title="总模型数" :value="stats.total" icon="Collection" color="#409EFF"/>
        </el-col>
        <el-col :span="6">
          <stat-card title="活跃模型" :value="stats.active" icon="SuccessFilled" color="#67C23A"/>
        </el-col>
        <el-col :span="6">
          <stat-card title="训练中" :value="stats.training" icon="Loading" color="#E6A23C"/>
        </el-col>
        <el-col :span="6">
          <stat-card title="平均准确率" :value="stats.accuracy" suffix="%" icon="TrendCharts"
                     color="#F56C6C"/>
        </el-col>
      </el-row>
    </div>

    <div class="model-filters">
      <el-form :model="filters" inline>
        <el-form-item label="模型类型">
          <el-select v-model="filters.model_type" placeholder="请选择模型类型" clearable>
            <el-option label="价格预测" value="price_prediction"/>
            <el-option label="产量预测" value="yield_prediction"/>
            <el-option label="病害检测" value="disease_detection"/>
            <el-option label="市场分析" value="market_analysis"/>
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="请选择状态" clearable>
            <el-option label="训练中" value="training"/>
            <el-option label="已激活" value="active"/>
            <el-option label="未激活" value="inactive"/>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadModels">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 网络错误提示 -->
    <div v-if="networkError" class="network-error">
      <el-alert
        title="网络连接错误"
        description="无法连接到后端服务，请检查后端服务是否已启动。"
        type="error"
        :closable="false"
        show-icon
      />
      <div class="error-actions">
        <el-button type="primary" @click="loadModels">重试</el-button>
        <el-button @click="useMockData">使用演示数据</el-button>
      </div>
    </div>

    <div class="model-list">
      <el-table :data="models" v-loading="loading">
        <el-table-column prop="name" label="模型名称" min-width="150">
          <template #default="{ row }">
            <div class="model-name">
              <el-icon class="model-icon">
                <DataAnalysis/>
              </el-icon>
              <span>{{ row.name }}</span>
              <el-tag v-if="row.status === 'active'" type="success" size="small">已激活</el-tag>
              <el-tag v-else-if="row.status === 'training'" type="warning" size="small">训练中
              </el-tag>
              <el-tag v-else type="info" size="small">未激活</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="model_type" label="模型类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getModelTypeTag(row.model_type)">
              {{ getModelTypeText(row.model_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="version" label="版本" width="80"/>

        <el-table-column prop="accuracy" label="准确率" width="100">
          <template #default="{ row }">
            <span v-if="row.accuracy">{{ (row.accuracy * 100).toFixed(1) }}%</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="trainModel(row)">训练</el-button>
            <el-button size="small" type="primary" @click="predictModel(row)">预测</el-button>
            <el-dropdown @command="handleCommand($event, row)" trigger="click">
              <el-button size="small">
                更多
                <el-icon>
                  <ArrowDown/>
                </el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="detail">详情</el-dropdown-item>
                  <el-dropdown-item command="edit">编辑</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="debug-actions" v-if="false">
      <el-alert title="调试功能" type="warning" :closable="false">
        <template #default>
          <el-button-group>
            <el-button size="small" @click="testStatusUpdate('active')">
              设为已激活
            </el-button>
            <el-button size="small" @click="testStatusUpdate('training')">
              设为训练中
            </el-button>
            <el-button size="small" @click="testStatusUpdate('inactive')">
              设为未激活
            </el-button>
          </el-button-group>
        </template>
      </el-alert>
    </div>

    <!-- 创建模型对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建AI模型" width="600px">
      <model-form @success="handleFormSuccess" @cancel="showCreateDialog = false"/>
    </el-dialog>

    <!-- 编辑模型对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑AI模型" width="600px">
      <model-form
        :model-id="selectedModel?.id"
        @success="handleEditSuccess"
        @cancel="showEditDialog = false"
      />
    </el-dialog>

    <!-- 模型详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="模型详情" width="700px">
      <model-detail :model="selectedModel" @close="showDetailDialog = false"
                    @edit="editModelFromDetail"/>
    </el-dialog>

    <!-- 训练对话框 -->
    <training-dialog
      :visible="showTrainingDialog"
      :model="selectedModel"
      @update:visible="showTrainingDialog = $event"
      @success="handleTrainingSuccess"
    />

    <!-- 预测对话框 -->
    <prediction-dialog
      :visible="showPredictionDialog"
      :model="selectedModel"
      @update:visible="showPredictionDialog = $event"
      @success="handlePredictionSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'  // 添加 watch 导入
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, DataAnalysis, ArrowDown } from '@element-plus/icons-vue'
import { useAIStore } from '../stores/ai'
import { aiAPI } from '../api/ai'
import ModelForm from '../components/ai/ModelForm.vue'
import ModelDetail from '../components/ai/ModelDetail.vue'
import TrainingDialog from '../components/ai/TrainingDialog.vue'
import PredictionDialog from '../components/ai/PredictionDialog.vue'
import StatCard from '../components/common/StatCard.vue'

const aiStore = useAIStore()

const loading = ref(false)
const networkError = ref(false)
const models = ref([])
const stats = ref({
  total: 0,
  active: 0,
  training: 0,
  accuracy: 0
})
const filters = ref({
  model_type: '',
  status: ''
})
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const showTrainingDialog = ref(false)
const showPredictionDialog = ref(false)
const selectedModel = ref(null)

// 添加缺失的函数
const getStatusText = (status) => {
  const textMap = {
    'active': '已激活',
    'training': '训练中',
    'inactive': '未激活',
    'error': '错误'
  }
  return textMap[status] || status
}

// 添加测试方法
const testStatusUpdate = async (status) => {
  if (models.value.length === 0) {
    ElMessage.warning('没有模型可更新')
    return
  }

  const model = models.value[0]
  try {
    await aiStore.updateModelStatus(model.id, status)
    ElMessage.success(`模型状态已更新为: ${getStatusText(status)}`)
    // 重新加载模型列表以确认状态更新
    await loadModels()
  } catch (error) {
    ElMessage.error('状态更新失败: ' + error.message)
  }
}

const loadModels = async () => {
  loading.value = true
  networkError.value = false
  try {
    console.log('开始加载模型列表...')
    const response = await aiAPI.getModels(filters.value)
    console.log('模型列表API完整响应:', response)

    // 修复：API响应直接就是数组，没有嵌套的data属性
    if (response) {
      // 如果API直接返回数组
      if (Array.isArray(response)) {
        models.value = response
        console.log('成功加载模型列表(直接数组):', models.value)
      }
      // 如果API返回 {data: [...]}
      else if (response.data && Array.isArray(response.data)) {
        models.value = response.data
        console.log('成功加载模型列表(data数组):', models.value)
      }
      // 如果API返回 {data: {results: [...]}}
      else if (response.data && response.data.results && Array.isArray(response.data.results)) {
        models.value = response.data.results
        console.log('成功加载模型列表(results数组):', models.value)
      }
      // 如果API返回其他格式
      else {
        console.warn('模型列表响应格式未知，尝试提取数据:', response)
        // 尝试从响应中提取数组数据
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
        models.value = findArray(response)
        console.log('提取的模型列表:', models.value)
      }
    } else {
      models.value = []
      console.error('模型列表API响应为空')
      ElMessage.error('加载模型列表失败: API响应为空')
    }

    // 计算统计信息
    updateStats()

    if (models.value.length > 0) {
      ElMessage.success(`加载了 ${models.value.length} 个模型`)
    } else {
      ElMessage.info('没有找到模型')
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
    networkError.value = true
    ElMessage.error('加载模型列表失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}

// 将 watch 移到函数外部
watch(models, (newModels) => {
  console.log('模型列表发生变化:', newModels.map(m => ({
    id: m.id,
    name: m.name,
    status: m.status,
    accuracy: m.accuracy
  })))
}, { deep: true })

const updateStats = () => {
  stats.value.total = models.value.length
  stats.value.active = models.value.filter(m => m.status === 'active').length
  stats.value.training = models.value.filter(m => m.status === 'training').length

  const activeModels = models.value.filter(m => m.accuracy)
  if (activeModels.length > 0) {
    const totalAccuracy = activeModels.reduce((sum, m) => sum + m.accuracy, 0)
    stats.value.accuracy = (totalAccuracy / activeModels.length * 100).toFixed(1)
  } else {
    stats.value.accuracy = 0
  }
}

const useMockData = () => {
  console.log('使用演示数据')
  models.value = [
    {
      id: 1,
      name: '水果价格预测模型',
      model_type: 'price_prediction',
      description: '基于历史数据的水果价格预测模型',
      version: '1.0',
      status: 'active',
      accuracy: 0.85,
      feature_columns: ['season', 'temperature', 'rainfall', 'supply', 'demand'],
      target_column: 'price',
      training_data: 1,
      training_config: {
        n_estimators: 100,
        max_depth: 10,
        test_size: 0.2
      },
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-20T14:45:00Z'
    },
    {
      id: 2,
      name: '农作物产量预测',
      model_type: 'yield_prediction',
      description: '预测主要农作物的产量',
      version: '1.1',
      status: 'training',
      accuracy: null,
      feature_columns: ['soil_quality', 'fertilizer_usage', 'water_supply', 'sunlight_hours'],
      target_column: 'yield',
      training_data: 2,
      training_config: {
        n_estimators: 150,
        max_depth: 15,
        test_size: 0.25
      },
      created_at: '2024-01-18T09:15:00Z',
      updated_at: '2024-01-22T16:20:00Z'
    },
    {
      id: 3,
      name: '病害检测模型',
      model_type: 'disease_detection',
      description: '检测农作物病害',
      version: '1.2',
      status: 'inactive',
      accuracy: 0.92,
      feature_columns: ['leaf_color', 'spot_size', 'growth_rate', 'moisture'],
      target_column: 'disease_type',
      training_data: 3,
      training_config: {
        n_estimators: 200,
        max_depth: 20,
        test_size: 0.3
      },
      created_at: '2024-01-20T11:00:00Z',
      updated_at: '2024-01-25T09:30:00Z'
    }
  ]

  updateStats()
  networkError.value = false
  ElMessage.success('已加载演示数据')
}

const resetFilters = () => {
  filters.value = {
    model_type: '',
    status: ''
  }
  loadModels()
}

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

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const trainModel = (model) => {
  selectedModel.value = model
  showTrainingDialog.value = true
  console.log('打开训练对话框:', model)
}

const predictModel = (model) => {
  selectedModel.value = model
  showPredictionDialog.value = true
  console.log('打开预测对话框:', model)
}

const handleCommand = (command, model) => {
  console.log('处理命令:', command, model)
  selectedModel.value = model

  switch (command) {
    case 'detail':
      showModelDetail(model)
      break
    case 'edit':
      editModel(model)
      break
    case 'delete':
      deleteModel(model)
      break
  }
}

const showModelDetail = (model) => {
  selectedModel.value = model
  showDetailDialog.value = true
  console.log('显示模型详情:', model)
}

const editModel = (model) => {
  selectedModel.value = model
  showEditDialog.value = true
  console.log('编辑模型:', model)
}

const editModelFromDetail = (model) => {
  selectedModel.value = model
  showDetailDialog.value = false
  showEditDialog.value = true
  console.log('从详情页编辑模型:', model)
}

const deleteModel = async (model) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型"${model.name}"吗？此操作不可恢复。`,
      '确认删除',
      {type: 'warning'}
    )

    await aiAPI.deleteModel(model.id)
    ElMessage.success('删除成功')
    loadModels()
  } catch (error) {
    // 用户取消删除
    console.log('用户取消删除操作')
  }
}

const handleFormSuccess = () => {
  showCreateDialog.value = false
  loadModels()
  ElMessage.success('模型创建成功')
}

const handleEditSuccess = () => {
  showEditDialog.value = false
  loadModels()
  ElMessage.success('模型更新成功')
}

const handleTrainingSuccess = () => {
  showTrainingDialog.value = false
  loadModels()
  ElMessage.success('模型训练完成')
}

const handlePredictionSuccess = () => {
  showPredictionDialog.value = false
  loadModels()
  ElMessage.success('预测完成')
}

onMounted(() => {
  console.log('AIModels页面挂载')
  loadModels()
})
</script>

<style scoped>
.ai-models-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.model-stats {
  margin-bottom: 20px;
}

.model-filters {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.model-list {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-icon {
  color: #409EFF;
  font-size: 16px;
}

.text-muted {
  color: #909399;
}

.network-error {
  margin-bottom: 20px;
}

.error-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}
</style>
