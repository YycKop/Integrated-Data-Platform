<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import {
  DataBoard,
  Collection,
  SetUp,
  PieChart,
  Monitor,
  Cpu,
  Refresh
} from '@element-plus/icons-vue'

// 导入所有API
import { datasetsAPI } from '../api/datasets'
import { aiAPI } from '../api/ai'
import { processingAPI } from '../api/processing'
import { visualizationAPI } from '../api/visualization'

const authStore = useAuthStore()
const activeTab = ref('dataSources')
const loading = ref(false)

// 用户数据状态
const userData = reactive({
  dataSources: [],
  datasets: [],
  pipelines: [],
  visualizations: [],
  dashboards: [],
  aiModels: []
})

// 获取用户创建的数据
const fetchUserData = async () => {
  loading.value = true
  try {
    const currentUserId = authStore.user?.id
    const currentUsername = authStore.user?.username
    console.log('🔧 [Profile] 当前用户ID:', currentUserId)
    console.log('🔧 [Profile] 当前用户名:', currentUsername)

    // 调用所有API - 使用正确的API路径
    const [
      dataSourcesResponse,
      datasetsResponse,
      pipelinesResponse,
      visualizationsResponse,
      dashboardsResponse,
      aiModelsResponse
    ] = await Promise.allSettled([
      datasetsAPI.getDataSources(),
      datasetsAPI.getDatasets(),
      // 使用正确的处理流程API
      processingAPI.getPipelines(),
      // 使用正确的可视化API
      visualizationAPI.getVisualizations(),
      // 使用正确的看板API
      visualizationAPI.getDashboards(),
      aiAPI.getModels()
    ])

    console.log('🔧 [Profile] 所有API响应:', {
      dataSources: dataSourcesResponse,
      datasets: datasetsResponse,
      pipelines: pipelinesResponse,
      visualizations: visualizationsResponse,
      dashboards: dashboardsResponse,
      aiModels: aiModelsResponse
    })

    // 通用过滤函数
    const filterByCreator = (items, itemName = '') => {
      return Array.isArray(items)
        ? items.filter(item => {
            const createdBy = item.created_by || item.user || item.created_by_user

            console.log(`🔧 [Profile] ${itemName} ${item.id} 创建者:`, createdBy, '类型:', typeof createdBy)

            if (typeof createdBy === 'object' && createdBy !== null) {
              return createdBy.id === currentUserId || createdBy.username === currentUsername
            } else if (typeof createdBy === 'string') {
              return createdBy === currentUsername
            } else if (typeof createdBy === 'number') {
              return createdBy === currentUserId
            }

            return false
          })
        : []
    }

    // 处理数据源
    if (dataSourcesResponse.status === 'fulfilled') {
      const allDataSources = dataSourcesResponse.value.data || dataSourcesResponse.value
      userData.dataSources = filterByCreator(allDataSources, '数据源')
      console.log('🔧 [Profile] 过滤后的数据源:', userData.dataSources)
    }

    // 处理数据集
    if (datasetsResponse.status === 'fulfilled') {
      const allDatasets = datasetsResponse.value.data || datasetsResponse.value
      userData.datasets = filterByCreator(allDatasets, '数据集')
      console.log('🔧 [Profile] 过滤后的数据集:', userData.datasets)
    }

    // 处理处理流程
    if (pipelinesResponse.status === 'fulfilled') {
      const allPipelines = pipelinesResponse.value.data || pipelinesResponse.value
      userData.pipelines = filterByCreator(allPipelines, '处理流程')
      console.log('🔧 [Profile] 过滤后的处理流程:', userData.pipelines)
    } else {
      console.warn('🔧 [Profile] 处理流程API不可用:', pipelinesResponse.reason)
      // 尝试使用备用API
      try {
        console.log('🔧 [Profile] 尝试使用处理任务API...')
        const processingTasksResponse = await processingAPI.getProcessingTasks()
        if (processingTasksResponse.status === 200) {
          const allTasks = processingTasksResponse.data || processingTasksResponse
          userData.pipelines = filterByCreator(allTasks, '处理任务')
          console.log('🔧 [Profile] 从处理任务API获取的数据:', userData.pipelines)
        }
      } catch (error) {
        console.warn('🔧 [Profile] 处理任务API也失败:', error)
        userData.pipelines = []
      }
    }

    // 处理可视化
    if (visualizationsResponse.status === 'fulfilled') {
      const allVisualizations = visualizationsResponse.value.data || visualizationsResponse.value
      userData.visualizations = filterByCreator(allVisualizations, '可视化')
      console.log('🔧 [Profile] 过滤后的可视化:', userData.visualizations)
    } else {
      console.warn('🔧 [Profile] 可视化API不可用:', visualizationsResponse.reason)
      userData.visualizations = []
    }

    // 处理看板
    if (dashboardsResponse.status === 'fulfilled') {
      const allDashboards = dashboardsResponse.value.data || dashboardsResponse.value
      userData.dashboards = filterByCreator(allDashboards, '看板')
      console.log('🔧 [Profile] 过滤后的看板:', userData.dashboards)
    } else {
      console.warn('🔧 [Profile] 看板API不可用:', dashboardsResponse.reason)
      userData.dashboards = []
    }

    // 处理AI模型
    if (aiModelsResponse.status === 'fulfilled') {
      const allModels = aiModelsResponse.value.data || aiModelsResponse.value
      userData.aiModels = filterByCreator(allModels, 'AI模型')
      console.log('🔧 [Profile] 过滤后的AI模型:', userData.aiModels)
    }

    console.log('🔧 [Profile] 最终用户数据:', userData)

    // 如果没有数据，显示提示信息
    const totalItems = Object.values(userData).reduce((sum, arr) => sum + arr.length, 0)
    if (totalItems === 0) {
      ElMessage.info('您还没有创建任何数据')
    } else {
      ElMessage.success('数据加载成功')
    }
  } catch (error) {
    console.error('🔧 [Profile] 获取用户数据失败:', error)
    ElMessage.error('数据加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshUserData = () => {
  fetchUserData()
}

// 工具函数
const getRoleTag = (role) => {
  const roleMap = {
    admin: 'danger',
    analyst: 'warning',
    viewer: 'success'
  }
  return roleMap[role] || 'info'
}

const getRoleText = (role) => {
  const roleMap = {
    admin: '管理员',
    analyst: '数据分析师',
    viewer: '查看者'
  }
  return roleMap[role] || role
}

const getDataSourceTypeTag = (type) => {
  const typeMap = {
    database: 'primary',
    file: 'success',
    api: 'warning'
  }
  return typeMap[type] || 'info'
}

const getDataSourceTypeText = (type) => {
  const typeMap = {
    database: '数据库',
    file: '文件',
    api: 'API'
  }
  return typeMap[type] || type
}

const getDatasetTypeTag = (type) => {
  const typeMap = {
    csv: 'success',
    json: 'warning',
    excel: 'primary',
    database: 'info'
  }
  return typeMap[type] || 'info'
}

const getPipelineStatusTag = (status) => {
  const statusMap = {
    active: 'success',
    draft: 'info',
    error: 'danger',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    pending: 'warning'
  }
  return statusMap[status] || 'info'
}

const getPipelineStatusText = (status) => {
  const statusMap = {
    active: '活跃',
    draft: '草稿',
    error: '错误',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    pending: '等待中'
  }
  return statusMap[status] || status
}

const getVisualizationTypeTag = (type) => {
  const typeMap = {
    line: 'primary',
    bar: 'success',
    pie: 'warning',
    scatter: 'info',
    table: 'default',
    area: 'primary',
    radar: 'success'
  }
  return typeMap[type] || 'info'
}

const getVisualizationTypeText = (type) => {
  const typeMap = {
    line: '折线图',
    bar: '柱状图',
    pie: '饼图',
    scatter: '散点图',
    table: '表格',
    area: '面积图',
    radar: '雷达图'
  }
  return typeMap[type] || type
}

const getDashboardStatusTag = (isPublic) => {
  return isPublic ? 'success' : 'info'
}

const getDashboardStatusText = (isPublic) => {
  return isPublic ? '公开' : '私有'
}

const getAIModelStatusTag = (status) => {
  const statusMap = {
    active: 'success',
    training: 'warning',
    error: 'danger',
    draft: 'info'
  }
  return statusMap[status] || 'info'
}

const getAIModelStatusText = (status) => {
  const statusMap = {
    active: '已训练',
    training: '训练中',
    error: '训练失败',
    draft: '草稿'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch {
    return '未知'
  }
}

// 获取图表数量
const getChartCount = (dashboard) => {
  return dashboard.charts?.length ||
         dashboard.visualizations?.length ||
         dashboard.items?.length ||
         0
}

onMounted(() => {
  fetchUserData()
})
</script>

<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人信息</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>基本信息</span>
          </template>
          <div class="user-info-detail">
            <div class="info-item">
              <span class="label">用户名：</span>
              <span class="value">{{ authStore.user?.username }}</span>
            </div>
            <div class="info-item">
              <span class="label">角色：</span>
              <el-tag :type="getRoleTag(authStore.user?.role)">
                {{ getRoleText(authStore.user?.role) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">邮箱：</span>
              <span class="value">{{ authStore.user?.email || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="label">注册时间：</span>
              <span class="value">{{ formatDate(authStore.user?.created_at) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 用户创建的数据信息 -->
        <el-card class="user-data-section">
          <template #header>
            <span>我的数据</span>
            <el-button
              type="primary"
              link
              @click="refreshUserData"
              :loading="loading"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </template>
          <div class="user-data-content">
            <el-tabs v-model="activeTab" type="card">
              <!-- 数据源 -->
              <el-tab-pane label="数据源" name="dataSources">
                <div class="data-list">
                  <div v-if="loading" class="loading-state">
                    <el-skeleton :rows="3" animated />
                  </div>
                  <div v-else-if="userData.dataSources.length === 0" class="empty-state">
                    <el-empty description="暂无创建的数据源" />
                  </div>
                  <div v-else class="data-items">
                    <div
                      v-for="source in userData.dataSources"
                      :key="source.id"
                      class="data-item"
                    >
                      <div class="data-item-header">
                        <el-icon class="data-icon"><DataBoard /></el-icon>
                        <span class="data-name">{{ source.name }}</span>
                        <el-tag size="small" :type="getDataSourceTypeTag(source.type)">
                          {{ getDataSourceTypeText(source.type) }}
                        </el-tag>
                      </div>
                      <div class="data-item-meta">
                        <span>创建时间: {{ formatDate(source.created_at) }}</span>
                        <span>状态: {{ source.status || '未知' }}</span>
                      </div>
                      <div class="data-item-description">
                        {{ source.description || '暂无描述' }}
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 数据集 -->
              <el-tab-pane label="数据集" name="datasets">
                <div class="data-list">
                  <div v-if="loading" class="loading-state">
                    <el-skeleton :rows="3" animated />
                  </div>
                  <div v-else-if="userData.datasets.length === 0" class="empty-state">
                    <el-empty description="暂无创建的数据集" />
                  </div>
                  <div v-else class="data-items">
                    <div
                      v-for="dataset in userData.datasets"
                      :key="dataset.id"
                      class="data-item"
                    >
                      <div class="data-item-header">
                        <el-icon class="data-icon"><Collection /></el-icon>
                        <span class="data-name">{{ dataset.name }}</span>
                        <el-tag size="small" :type="getDatasetTypeTag(dataset.data_type)">
                          {{ dataset.data_type || '未知' }}
                        </el-tag>
                      </div>
                      <div class="data-item-meta">
                        <span>创建时间: {{ formatDate(dataset.created_at) }}</span>
                        <span>数据源: {{ dataset.data_source?.name || '未知' }}</span>
                      </div>
                      <div class="data-item-description">
                        {{ dataset.description || '暂无描述' }}
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 处理流程 -->
              <el-tab-pane label="处理流程" name="pipelines">
                <div class="data-list">
                  <div v-if="loading" class="loading-state">
                    <el-skeleton :rows="3" animated />
                  </div>
                  <div v-else-if="userData.pipelines.length === 0" class="empty-state">
                    <el-empty description="暂无创建的处理流程" />
                  </div>
                  <div v-else class="data-items">
                    <div
                      v-for="pipeline in userData.pipelines"
                      :key="pipeline.id"
                      class="data-item"
                    >
                      <div class="data-item-header">
                        <el-icon class="data-icon"><SetUp /></el-icon>
                        <span class="data-name">{{ pipeline.name }}</span>
                        <el-tag size="small" :type="getPipelineStatusTag(pipeline.status)">
                          {{ getPipelineStatusText(pipeline.status) }}
                        </el-tag>
                      </div>
                      <div class="data-item-meta">
                        <span>创建时间: {{ formatDate(pipeline.created_at) }}</span>
                        <span>最后执行: {{ formatDate(pipeline.last_executed) || '从未执行' }}</span>
                      </div>
                      <div class="data-item-description">
                        {{ pipeline.description || '暂无描述' }}
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 数据可视化 -->
              <el-tab-pane label="数据可视化" name="visualizations">
                <div class="data-list">
                  <div v-if="loading" class="loading-state">
                    <el-skeleton :rows="3" animated />
                  </div>
                  <div v-else-if="userData.visualizations.length === 0" class="empty-state">
                    <el-empty description="暂无创建的可视化" />
                  </div>
                  <div v-else class="data-items">
                    <div
                      v-for="viz in userData.visualizations"
                      :key="viz.id"
                      class="data-item"
                    >
                      <div class="data-item-header">
                        <el-icon class="data-icon">
                          <PieChart/>
                        </el-icon>
                        <span class="data-name">{{ viz.name }}</span>
                        <el-tag size="small" :type="getVisualizationTypeTag(viz.chart_type)">
                          {{ getVisualizationTypeText(viz.chart_type) }}
                        </el-tag>
                      </div>
                      <div class="data-item-meta">
                        <span>创建时间: {{ formatDate(viz.created_at) }}</span>
                        <span>数据集: {{ viz.dataset?.name || '未知' }}</span>
                      </div>
                      <div class="data-item-description">
                        {{ viz.description || '暂无描述' }}
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 数据看板 -->
              <el-tab-pane label="数据看板" name="dashboards">
                <div class="data-list">
                  <div v-if="loading" class="loading-state">
                    <el-skeleton :rows="3" animated/>
                  </div>
                  <div v-else-if="userData.dashboards.length === 0" class="empty-state">
                    <el-empty description="暂无创建的看板"/>
                  </div>
                  <div v-else class="data-items">
                    <div
                      v-for="dashboard in userData.dashboards"
                      :key="dashboard.id"
                      class="data-item"
                    >
                      <div class="data-item-header">
                        <el-icon class="data-icon">
                          <Monitor/>
                        </el-icon>
                        <span class="data-name">{{ dashboard.name }}</span>
                        <el-tag
                          size="small"
                          :type="getDashboardStatusTag(dashboard.is_public)"
                        >
                          {{ getDashboardStatusText(dashboard.is_public) }}
                        </el-tag>
                      </div>
                      <div class="data-item-meta">
                        <span>创建时间: {{ formatDate(dashboard.created_at) }}</span>
                        <span>图表数: {{ getChartCount(dashboard) }} 个</span>
                      </div>
                      <div class="data-item-description">
                        {{ dashboard.description || '暂无描述' }}
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <!-- AI模型 -->
              <el-tab-pane label="AI模型" name="aiModels">
                <div class="data-list">
                  <div v-if="loading" class="loading-state">
                    <el-skeleton :rows="3" animated/>
                  </div>
                  <div v-else-if="userData.aiModels.length === 0" class="empty-state">
                    <el-empty description="暂无创建的AI模型"/>
                  </div>
                  <div v-else class="data-items">
                    <div
                      v-for="model in userData.aiModels"
                      :key="model.id"
                      class="data-item"
                    >
                      <div class="data-item-header">
                        <el-icon class="data-icon">
                          <Cpu/>
                        </el-icon>
                        <span class="data-name">{{ model.name }}</span>
                        <el-tag size="small" :type="getAIModelStatusTag(model.status)">
                          {{ getAIModelStatusText(model.status) }}
                        </el-tag>
                      </div>
                      <div class="data-item-meta">
                        <span>创建时间: {{ formatDate(model.created_at) }}</span>
                        <span v-if="model.accuracy">准确率: {{
                            (model.accuracy * 100).toFixed(2)
                          }}%</span>
                        <span v-else>准确率: 未训练</span>
                      </div>
                      <div class="data-item-description">
                        {{ model.description || '暂无描述' }}
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <!-- 统计概览 -->
        <el-card>
          <template #header>
            <span>数据统计</span>
          </template>
          <div class="stats-overview">
            <div class="stat-item">
              <div class="stat-icon data-source">
                <el-icon>
                  <DataBoard/>
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userData.dataSources.length }}</div>
                <div class="stat-label">数据源</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon dataset">
                <el-icon>
                  <Collection/>
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userData.datasets.length }}</div>
                <div class="stat-label">数据集</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon pipeline">
                <el-icon>
                  <SetUp/>
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userData.pipelines.length }}</div>
                <div class="stat-label">处理流程</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon visualization">
                <el-icon>
                  <PieChart/>
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userData.visualizations.length }}</div>
                <div class="stat-label">可视化</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon dashboard">
                <el-icon>
                  <Monitor/>
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userData.dashboards.length }}</div>
                <div class="stat-label">数据看板</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon ai-model">
                <el-icon>
                  <Cpu/>
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userData.aiModels.length }}</div>
                <div class="stat-label">AI模型</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
/* 样式保持不变 */
.profile-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.user-info-detail .info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.user-info-detail .info-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.user-info-detail .label {
  color: #606266;
  font-weight: 500;
  min-width: 100px;
}

.user-info-detail .value {
  color: #303133;
  text-align: right;
}

.user-data-section {
  margin-top: 20px;
}

.data-list {
  min-height: 200px;
}

.data-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.data-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.data-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.data-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.data-icon {
  font-size: 16px;
  color: #409eff;
}

.data-name {
  font-weight: 500;
  flex: 1;
}

.data-item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.data-item-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.empty-state {
  padding: 40px 0;
}

.loading-state {
  padding: 20px 0;
}

.stats-overview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.stat-icon.data-source {
  background-color: #409eff;
}

.stat-icon.dataset {
  background-color: #67c23a;
}

.stat-icon.pipeline {
  background-color: #e6a23c;
}

.stat-icon.visualization {
  background-color: #f56c6c;
}

.stat-icon.dashboard {
  background-color: #909399;
}

.stat-icon.ai-model {
  background-color: #9c27b0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}
</style>
