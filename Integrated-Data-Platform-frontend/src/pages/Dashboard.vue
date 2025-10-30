<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/pages/Dashboard.vue -->
<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2>数据仪表板</h2>
      <p class="welcome-text">欢迎回来，{{ authStore.user?.username }}！</p>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon data-source-icon">
              <el-icon>
                <Collection/>
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.dataSources }}</div>
              <div class="stat-label">数据源</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon dataset-icon">
              <el-icon>
                <DataBoard/>
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.datasets }}</div>
              <div class="stat-label">数据集</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon pipeline-icon">
              <el-icon>
                <SetUp/>
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.pipelines }}</div>
              <div class="stat-label">处理流程</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon visualization-icon">
              <el-icon>
                <TrendCharts/>
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.visualizations }}</div>
              <div class="stat-label">可视化</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新的布局：左侧最新数据，右侧固定面板 -->
    <el-row :gutter="20" class="main-content-row">
      <!-- 左侧：最新数据部分 -->
      <el-col :span="18" class="left-content">
        <!-- 第一行：数据源和数据集 -->
        <el-row :gutter="20" class="charts-row">
          <!-- 最新数据源 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>最新数据源</span>
                  <el-button type="text" @click="$router.push('/data-sources')">查看全部</el-button>
                </div>
              </template>
              <el-table :data="recentDataSources" v-loading="loading.dataSources" height="300">
                <el-table-column prop="name" label="数据源名称"/>
                <el-table-column prop="type" label="类型" width="100">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getDataSourceTypeTag(row.type)">
                      {{ getDataSourceTypeText(row.type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>

          <!-- 最新数据集 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>最新数据集</span>
                  <el-button type="text" @click="$router.push('/datasets')">查看全部</el-button>
                </div>
              </template>
              <el-table :data="recentDatasets" v-loading="loading.datasets" height="300">
                <el-table-column prop="name" label="数据集名称"/>
                <el-table-column prop="record_count" label="记录数" width="80">
                  <template #default="{ row }">
                    <span>{{ row.record_count || row.data_count || 0 }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getDatasetStatusTag(row.status)">
                      {{ getDatasetStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <!-- 第二行：处理流程和可视化 -->
        <el-row :gutter="20" class="charts-row">
          <!-- 最新处理流程 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>最新处理流程</span>
                  <el-button type="text" @click="$router.push('/processing')">查看全部</el-button>
                </div>
              </template>
              <el-table :data="recentPipelines" v-loading="loading.pipelines" height="300">
                <el-table-column prop="name" label="流程名称"/>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getPipelineStatusTag(row.status)">
                      {{ getPipelineStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>

          <!-- 最新可视化 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>最新可视化</span>
                  <el-button type="text" @click="$router.push('/visualization')">查看全部
                  </el-button>
                </div>
              </template>
              <el-table :data="recentVisualizations" v-loading="loading.visualizations"
                        height="300">
                <el-table-column prop="name" label="可视化名称"/>
                <el-table-column prop="type" label="类型" width="100">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getVisualizationTypeTag(row.type)">
                      {{ getVisualizationTypeText(row.type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <!-- 第三行：最新数据看板 -->
        <el-row :gutter="20" class="charts-row">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>最新数据看板</span>
                  <el-button type="text" @click="$router.push('/dashboards')">查看全部</el-button>
                </div>
              </template>
              <el-table :data="recentDashboards" v-loading="loading.dashboards" height="300">
                <el-table-column prop="name" label="看板名称"/>
                <el-table-column prop="chart_count" label="图表数" width="80">
                  <template #default="{ row }">
                    <span>{{ getChartCount(row) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-col>

      <!-- 右侧：固定面板（快速操作 + 最近活动） -->
      <el-col :span="6" class="right-content">
        <!-- 快速操作卡片 -->
        <el-card class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/data-sources')"
                       class="quick-action-btn">
              <el-icon>
                <Collection/>
              </el-icon>
              <span class="btn-text">管理数据源</span>
            </el-button>
            <el-button type="success" @click="$router.push('/datasets')" class="quick-action-btn">
              <el-icon>
                <DataBoard/>
              </el-icon>
              <span class="btn-text">管理数据集</span>
            </el-button>
            <el-button type="warning" @click="$router.push('/processing')" class="quick-action-btn">
              <el-icon>
                <SetUp/>
              </el-icon>
              <span class="btn-text">数据处理</span>
            </el-button>
            <el-button type="info" @click="$router.push('/visualization')" class="quick-action-btn">
              <el-icon>
                <TrendCharts/>
              </el-icon>
              <span class="btn-text">数据可视化</span>
            </el-button>
            <el-button type="danger" @click="$router.push('/dashboards')" class="quick-action-btn">
              <el-icon>
                <Monitor/>
              </el-icon>
              <span class="btn-text">数据看板</span>
            </el-button>
            <el-button class="ai-model-btn quick-action-btn" @click="$router.push('/ai-models')">
              <el-icon>
                <Cpu/>
              </el-icon>
              <span class="btn-text">AI模型</span>
            </el-button>
            <el-button class="ai-analysis-btn quick-action-btn"
                       @click="$router.push('/ai-analysis')">
              <el-icon>
                <Opportunity/>
              </el-icon>
              <span class="btn-text">智能分析</span>
            </el-button>
          </div>
        </el-card>

        <!-- 最近活动卡片 -->
        <el-card class="activities-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
              <el-button type="text" size="small" @click="refreshActivities">
                <el-icon>
                  <Refresh/>
                </el-icon>
              </el-button>
            </div>
          </template>
          <div class="recent-activities">
            <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
              <div class="activity-avatar">
                <el-icon class="activity-icon" :class="activity.type">
                  <component :is="getIconComponent(activity.icon)"/>
                </el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-text">
                  <span class="user-name">{{ getActivityUserName(activity) }}</span>
                  <span class="action-text">{{ getActivityAction(activity) }}</span>
                  <span class="resource-name" v-if="getActivityResource(activity)">
                    "{{ getActivityResource(activity) }}"
                  </span>
                </div>
                <div class="activity-time">{{ formatRelativeTime(activity.timestamp) }}</div>
              </div>
            </div>
            <div v-if="recentActivities.length === 0" class="no-activities">
              <el-empty description="暂无活动记录" :image-size="60"/>
            </div>
            <div v-if="recentActivities.length > 0" class="activities-footer">
              <el-button type="text" size="small" @click="showAllActivities">
                查看全部活动
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import {useAuthStore} from '../stores/auth'
import {datasetsAPI} from '../api/datasets'
import {processingAPI} from '../api/processing'
import {visualizationAPI} from '../api/visualization'
import {activitiesAPI} from '../api/activities'
import {ElMessage} from 'element-plus'

import {
  Collection,
  DataBoard,
  SetUp,
  TrendCharts,
  Monitor,
  Cpu,
  Opportunity,
  Refresh
} from '@element-plus/icons-vue'

const authStore = useAuthStore()

const stats = reactive({
  dataSources: 0,
  datasets: 0,
  pipelines: 0,
  visualizations: 0
})

const loading = reactive({
  dataSources: false,
  datasets: false,
  pipelines: false,
  visualizations: false,
  dashboards: false,
  activities: false
})

const recentDataSources = ref([])
const recentDatasets = ref([])
const recentPipelines = ref([])
const recentVisualizations = ref([])
const recentDashboards = ref([])
const recentActivities = ref([])

const getDataSourceTypeTag = (type) => {
  const typeMap = {
    database: 'primary',
    api: 'success',
    file: 'warning',
    cloud: 'info'
  }
  return typeMap[type] || 'info'
}
const getChartCount = (dashboard) => {
  console.log('🔍 详细调试看板数据:', dashboard)

  if (!dashboard) {
    console.log('❌ 看板数据为空')
    return 0
  }

  // 🔥 关键修复：首先检查本地存储中是否有图表数据
  try {
    const localLayouts = JSON.parse(localStorage.getItem('dashboard_layouts') || '{}')
    const localLayout = localLayouts[dashboard.id]

    if (localLayout && localLayout.items && localLayout.items.length > 0) {
      console.log(`✅ 使用本地存储的图表数量: ${localLayout.items.length}`)
      return localLayout.items.length
    }
  } catch (error) {
    console.log('❌ 读取本地存储失败:', error)
  }

  // 打印所有字段以便调试
  console.log('📋 看板所有字段:', Object.keys(dashboard))

  // 多种可能的字段名尝试
  const possibleFields = [
    'charts_count',
    'chart_count',
    'visualization_count',
    'visualizations_count',
    'viz_count',
    'chart_count'
  ];

  // 检查直接字段
  for (const field of possibleFields) {
    if (dashboard[field] !== undefined && dashboard[field] !== null) {
      console.log(`✅ 找到数量字段 ${field}:`, dashboard[field]);
      return dashboard[field];
    }
  }

  // 检查数组长度
  const arrayFields = ['items_detail', 'items', 'visualizations', 'charts']
  for (const field of arrayFields) {
    if (dashboard[field] && Array.isArray(dashboard[field]) && dashboard[field].length > 0) {
      console.log(`✅ 使用数组字段 ${field} 长度:`, dashboard[field].length);
      return dashboard[field].length;
    }
  }

  // 检查嵌套结构
  if (dashboard.layout_config && dashboard.layout_config.items && Array.isArray(dashboard.layout_config.items) && dashboard.layout_config.items.length > 0) {
    console.log('✅ 使用 layout_config.items 长度:', dashboard.layout_config.items.length);
    return dashboard.layout_config.items.length;
  }

  console.log('❌ 未找到图表数量字段，返回0');
  return 0;
}
const getDataSourceTypeText = (type) => {
  const typeMap = {
    database: '数据库',
    api: 'API',
    file: '文件',
    cloud: '云存储'
  }
  return typeMap[type] || type
}

const getDatasetStatusTag = (status) => {
  const statusMap = {
    active: 'success',
    processing: 'warning',
    error: 'danger',
    ready: 'primary',
    idle: 'info'
  }
  return statusMap[status] || 'info'
}

const getDatasetStatusText = (status) => {
  const statusMap = {
    active: '活跃',
    processing: '处理中',
    error: '错误',
    ready: '就绪',
    idle: '空闲'
  }
  return statusMap[status] || status
}

const getPipelineStatusTag = (status) => {
  const statusMap = {
    active: 'success',
    running: 'warning',
    error: 'danger',
    idle: 'info',
    completed: 'success',
    processing: 'warning',
    failed: 'danger',
    pending: 'info'
  }
  return statusMap[status] || 'info'
}

const getPipelineStatusText = (status) => {
  const statusMap = {
    active: '活跃',
    running: '运行中',
    error: '错误',
    idle: '空闲',
    completed: '完成',
    processing: '处理中',
    failed: '失败',
    pending: '等待'
  }
  return statusMap[status] || status
}

const getVisualizationTypeTag = (type) => {
  const typeMap = {
    chart: 'primary',
    table: 'success',
    map: 'warning',
    dashboard: 'info'
  }
  return typeMap[type] || 'info'
}

const getVisualizationTypeText = (type) => {
  const typeMap = {
    chart: '图表',
    table: '表格',
    map: '地图',
    dashboard: '看板'
  }
  return typeMap[type] || type
}

// 图标组件映射
const iconComponents = {
  Collection,
  DataBoard,
  SetUp,
  TrendCharts,
  Monitor,
  Cpu,
  Opportunity,
  Refresh
}

// 获取图标组件
const getIconComponent = (iconName) => {
  return iconComponents[iconName] || DataBoard
}

// 刷新活动
const refreshActivities = async () => {
  loading.activities = true
  try {
    // 直接重新获取活动记录
    const activitiesResponse = await activitiesAPI.getRecentActivities({
      limit: 50
    })

    let activitiesData = []
    if (activitiesResponse && activitiesResponse.data) {
      activitiesData = activitiesResponse.data
    } else if (activitiesResponse && Array.isArray(activitiesResponse)) {
      activitiesData = activitiesResponse
    }

    recentActivities.value = transformActivitiesData(activitiesData)
    ElMessage.success('活动记录已刷新')
  } catch (error) {
    console.error('刷新活动记录失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    loading.activities = false
  }
}

// 查看全部活动
const showAllActivities = () => {
  ElMessage.info('全部活动功能开发中')
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return ''

  const now = new Date()
  const time = new Date(timestamp)
  const diffInSeconds = Math.floor((now - time) / 1000)

  if (diffInSeconds < 60) {
    return '刚刚'
  } else if (diffInSeconds < 3600) {
    return `${Math.floor(diffInSeconds / 60)}分钟前`
  } else if (diffInSeconds < 86400) {
    return `${Math.floor(diffInSeconds / 3600)}小时前`
  } else {
    return `${Math.floor(diffInSeconds / 86400)}天前`
  }
}

const loadStats = async () => {
  try {
    const [dataSources, datasets, pipelines, visualizations] = await Promise.allSettled([
      datasetsAPI.getDataSources().catch(() => ({data: []})),
      datasetsAPI.getDatasets().catch(() => ({data: []})),
      processingAPI.getPipelines().catch(() => ({data: []})),
      visualizationAPI.getVisualizations().catch(() => ({data: []}))
    ])

    stats.dataSources = dataSources.value?.data?.length || dataSources.value?.length || 0
    stats.datasets = datasets.value?.data?.length || datasets.value?.length || 0
    stats.pipelines = pipelines.value?.data?.length || pipelines.value?.length || 0
    stats.visualizations = visualizations.value?.data?.length || visualizations.value?.length || 0
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  }
}

const loadRecentData = async () => {
  loading.dataSources = true
  loading.datasets = true
  loading.pipelines = true
  loading.visualizations = true
  loading.dashboards = true
  loading.activities = true

  try {
    console.log("🔄 [Dashboard] 开始加载最近数据...")

    // 加载所有数据
    const [dataSourcesResult, datasetsResult, pipelinesResult, visualizationsResult, dashboardsResult] = await Promise.allSettled([
      datasetsAPI.getDataSources().catch(() => []),
      datasetsAPI.getDatasets().catch(() => []),
      processingAPI.getPipelines().catch(() => []),
      visualizationAPI.getVisualizations().catch(() => []),
      visualizationAPI.getDashboards().catch(() => [])
    ])

    // 🔥 修复：处理数据源
    const dataSourcesData = dataSourcesResult.value
    recentDataSources.value = dataSourcesData?.data?.slice(0, 5) ||
      dataSourcesData?.slice(0, 5) ||
      generateMockDataSources()

    // 🔥 修复：处理数据集
    const datasetsData = datasetsResult.value
    recentDatasets.value = datasetsData?.data?.slice(0, 5) ||
      datasetsData?.slice(0, 5) ||
      generateMockDatasets()

    // 🔥 修复：处理处理流程
    const pipelinesData = pipelinesResult.value
    recentPipelines.value = pipelinesData?.data?.slice(0, 5) ||
      pipelinesData?.slice(0, 5) ||
      generateMockPipelines()

    // 🔥 修复：处理可视化
    const visualizationsData = visualizationsResult.value
    recentVisualizations.value = visualizationsData?.data?.slice(0, 5) ||
      visualizationsData?.slice(0, 5) ||
      generateMockVisualizations()

    // 🔥 重点调试看板数据
    console.log("📊 [Dashboard] 看板API原始响应:", dashboardsResult)

    const dashboardsData = dashboardsResult.value
    console.log("📊 [Dashboard] 看板处理后的数据:", dashboardsData)

    // 处理数据看板
    recentDashboards.value = dashboardsData?.data?.slice(0, 5) ||
      dashboardsData?.slice(0, 5) ||
      generateMockDashboards()

    console.log("📊 [Dashboard] 最终显示的看板数据:", recentDashboards.value)

    // 🔥 新增：检查本地存储数据
    try {
      const localLayouts = JSON.parse(localStorage.getItem('dashboard_layouts') || '{}')
      console.log("💾 [Dashboard] 本地存储数据:", localLayouts)

      recentDashboards.value.forEach((dashboard, index) => {
        const localLayout = localLayouts[dashboard.id]
        console.log(`📊 看板 ${index + 1} (ID: ${dashboard.id}) 本地存储:`, localLayout)
      })
    } catch (error) {
      console.log('❌ 读取本地存储失败:', error)
    }

    // 对每个看板进行详细调试
    recentDashboards.value.forEach((dashboard, index) => {
      console.log(`📊 看板 ${index + 1}:`, dashboard)
      console.log(`🔍 看板 ${index + 1} 的所有字段:`, Object.keys(dashboard))

      // 检查所有可能的图表数量字段
      const countFields = ['charts_count', 'chart_count', 'visualization_count', 'visualizations_count', 'viz_count']
      countFields.forEach(field => {
        if (dashboard[field] !== undefined) {
          console.log(`✅ 找到字段 ${field}:`, dashboard[field])
        }
      })

      // 检查数组字段的长度
      const arrayFields = ['items_detail', 'items', 'visualizations', 'charts']
      arrayFields.forEach(field => {
        if (Array.isArray(dashboard[field])) {
          console.log(`✅ 数组字段 ${field} 长度:`, dashboard[field].length)
        }
      })
    })

    // 加载活动记录
    // 🔥 修复：增强活动记录加载
    // 加载活动记录 - 使用新的直接读取模式
    console.log("🔄 [Dashboard] 正在加载活动记录...")
    try {
      // 默认不使用直接读取，优先显示实时创建的活动记录
      const activitiesResponse = await activitiesAPI.getRecentActivities({
        limit: 50,
        direct_read: 'false'  // 优先使用数据库中的实时记录
      })

      console.log("📊 [Dashboard] 活动API响应:", activitiesResponse)

      let activitiesData = []
      if (activitiesResponse && activitiesResponse.data) {
        activitiesData = activitiesResponse.data
      } else if (activitiesResponse && Array.isArray(activitiesResponse)) {
        activitiesData = activitiesResponse
      } else if (activitiesResponse && activitiesResponse.results) {
        activitiesData = activitiesResponse.results
      } else {
        console.warn("⚠️ [Dashboard] 活动API返回数据格式异常:", activitiesResponse)
        activitiesData = []
      }

      console.log(`📊 [Dashboard] 获取到 ${activitiesData.length} 条活动记录`)

      // 如果活动记录为空，尝试使用直接读取模式
      if (activitiesData.length === 0) {
        console.log("🔄 活动记录为空，尝试使用直接读取模式...")
        try {
          const directReadResponse = await activitiesAPI.getRecentActivities({
            limit: 50,
            direct_read: 'true'
          })

          if (directReadResponse && directReadResponse.data) {
            activitiesData = directReadResponse.data
            console.log(`✅ 直接读取模式获取到 ${activitiesData.length} 条活动记录`)
          }
        } catch (directError) {
          console.error("❌ 直接读取模式失败:", directError)
        }
      }

      // 转换数据格式
      recentActivities.value = transformActivitiesData(activitiesData)
      console.log("✅ [Dashboard] 转换后的活动数据:", recentActivities.value)

    } catch (activityError) {
      console.error("❌ [Dashboard] 加载活动记录失败:", activityError)
      // 如果失败，使用模拟数据
      const mockActivities = generateMockActivities()
      recentActivities.value = mockActivities
    }
  } catch
    (error) {
    console.error('❌ [Dashboard] 加载最近数据失败:', error)
    // 如果失败，使用模拟数据
    recentDataSources.value = generateMockDataSources()
    recentDatasets.value = generateMockDatasets()
    recentPipelines.value = generateMockPipelines()
    recentVisualizations.value = generateMockVisualizations()
    recentDashboards.value = generateMockDashboards()

    // 在模拟数据中添加新创建的看板
    const mockActivities = generateMockActivities()
    mockActivities.unshift({
      id: Date.now(),
      type: 'primary',
      icon: 'Monitor',
      text: `${authStore.user?.username}用户创建了数据看板"tset1"`,
      timestamp: new Date().toISOString()
    })
    recentActivities.value = mockActivities
  } finally {
    loading.dataSources = false
    loading.datasets = false
    loading.pipelines = false
    loading.visualizations = false
    loading.dashboards = false
    loading.activities = false
  }
}

// 模拟数据生成函数
const generateMockDataSources = () => {
  return [
    {
      id: 1,
      name: '农产品销售数据库',
      type: 'database',
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      name: '气象数据API',
      type: 'api',
      created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      name: '土壤检测Excel',
      type: 'file',
      created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 4,
      name: '市场价格CSV',
      type: 'file',
      created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 5,
      name: '云存储备份',
      type: 'cloud',
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
    }
  ]
}

const generateMockDatasets = () => {
  return [
    {
      id: 1,
      name: '农产品销售数据',
      record_count: 12500,
      status: 'ready',
      created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      name: '气象监测数据',
      record_count: 8900,
      status: 'active',
      created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      name: '土壤质量数据',
      record_count: 5600,
      status: 'processing',
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 4,
      name: '市场价格数据',
      record_count: 15200,
      status: 'ready',
      created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 5,
      name: '生产记录数据',
      record_count: 7800,
      status: 'idle',
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
    }
  ]
}

const generateMockPipelines = () => {
  return [
    {
      id: 1,
      name: '数据清洗流程',
      status: 'completed',
      created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      name: '特征工程流程',
      status: 'running',
      created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      name: '数据标准化流程',
      status: 'completed',
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 4,
      name: '缺失值处理流程',
      status: 'error',
      created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 5,
      name: '数据聚合流程',
      status: 'idle',
      created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
    }
  ]
}

const generateMockVisualizations = () => {
  return [
    {
      id: 1,
      name: '销售趋势图',
      type: 'chart',
      created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      name: '产品质量分析表',
      type: 'table',
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      name: '区域分布地图',
      type: 'map',
      created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 4,
      name: '生产监控看板',
      type: 'dashboard',
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 5,
      name: '价格对比图',
      type: 'chart',
      created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString()
    }
  ]
}

const generateMockDashboards = () => {
  console.log("🎯 使用模拟看板数据")
  return [
    {
      id: 1,
      name: '销售分析看板',
      chart_count: 8,        // 主要字段
      charts_count: 8,       // 备用字段
      items_detail: [],      // 模拟数组字段
      created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      name: '生产监控看板',
      chart_count: 6,
      charts_count: 6,
      items_detail: [],
      created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      name: '质量评估看板',
      chart_count: 4,
      charts_count: 4,
      items_detail: [],
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 4,
      name: '库存管理看板',
      chart_count: 5,
      charts_count: 5,
      items_detail: [],
      created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 5,
      name: '预测分析看板',
      chart_count: 7,
      charts_count: 7,
      items_detail: [],
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
    }
  ]
}

const transformActivitiesData = (activities) => {
  if (!activities || !Array.isArray(activities)) {
    return []
  }

  return activities.map(activity => {
    // 确保活动数据有必要的字段
    const safeActivity = {
      id: activity.id || Math.random(),
      user_name: activity.user_name || activity.user?.username || '用户',
      activity_type: activity.activity_type || 'dataset_created',
      activity_type_display: activity.activity_type_display || getActivityTypeDisplay(activity.activity_type),
      description: activity.description || '',  // 直接使用后端返回的描述
      resource_name: activity.resource_name || '',
      timestamp: activity.timestamp || activity.created_at || new Date().toISOString()
    }

    const {icon, type} = getActivityIconAndType(safeActivity.activity_type)

    // 直接使用后端返回的描述，不再重新生成
    const displayText = safeActivity.description

    return {
      id: safeActivity.id,
      type: type,
      icon: icon,
      text: displayText,  // 直接使用标准格式的描述
      timestamp: safeActivity.timestamp,
      _raw: safeActivity
    }
  })
}


const getActivityIconAndType = (activityType) => {
  const typeMap = {
    'data_source_created': {icon: 'Collection', type: 'primary'},
    'dataset_created': {icon: 'DataBoard', type: 'success'},
    'pipeline_executed': {icon: 'SetUp', type: 'warning'},
    'visualization_created': {icon: 'TrendCharts', type: 'info'},
    'dashboard_created': {icon: 'Monitor', type: 'primary'},
    'ai_model_trained': {icon: 'Cpu', type: 'ai'},
    'data_processed': {icon: 'SetUp', type: 'success'}
  }

  return typeMap[activityType] || {icon: 'DataBoard', type: 'info'}
}
const getActivityTypeDisplay = (activityType) => {
  const typeMap = {
    'data_source_created': '创建数据源',
    'dataset_created': '创建数据集',
    'pipeline_executed': '执行处理流程',
    'visualization_created': '创建可视化',
    'dashboard_created': '创建看板',
    'ai_model_trained': '训练AI模型',
    'data_processed': '数据处理完成'
  }
  return typeMap[activityType] || '执行了操作'
}

const getActivityUserName = (activity) => {
  return activity._raw?.user_name || '用户'
}

const getActivityAction = (activity) => {
  return activity._raw?.activity_type_display || '执行了操作'
}

const getActivityResource = (activity) => {
  return activity._raw?.resource_name || ''
}

const generateMockActivities = () => {
  return [
    {
      id: 1,
      type: 'success',
      icon: 'DataBoard',
      text: 'admin 创建了数据集 "农产品销售数据"',  // 使用标准格式
      timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      type: 'warning',
      icon: 'SetUp',
      text: 'yyckop 执行了处理流程 "数据清洗流程"',  // 使用标准格式
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      type: 'info',
      icon: 'TrendCharts',
      text: 'admin 创建了可视化 "月度销售趋势"',  // 使用标准格式
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 4,
      type: 'primary',
      icon: 'Collection',
      text: 'yyckop 创建了数据源 "数据库连接"',  // 使用标准格式
      timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 5,
      type: 'ai',
      icon: 'Cpu',
      text: 'admin 训练了AI模型 "价格预测模型"',  // 使用标准格式
      timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
    }
  ]
}
onMounted(() => {
  console.log("🚀 [Dashboard] 组件已挂载，开始加载数据...")
  loadStats()
  loadRecentData()
})
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.welcome-text {
  color: #666;
  margin-top: 8px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 16px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.data-source-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.dataset-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.pipeline-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.visualization-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 新的布局样式 */
.main-content-row {
  margin-bottom: 24px;
}

.left-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 20px;
  height: fit-content;
}

/* 快速操作卡片样式 */
.quick-actions-card {
  position: sticky;
  top: 20px;
  z-index: 10;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  height: 44px;
  padding: 0 16px;
  margin: 0;
  text-align: left;
}

.quick-action-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
  flex-shrink: 0;
}

.btn-text {
  flex: 1;
  text-align: left;
  font-size: 14px;
}

/* AI相关按钮样式 */
.ai-model-btn {
  background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%);
  border-color: #9c27b0;
  color: white;
}

.ai-model-btn:hover {
  background: linear-gradient(135deg, #8e24aa 0%, #5e35b1 100%);
  border-color: #8e24aa;
  color: white;
}

.ai-analysis-btn {
  background: linear-gradient(135deg, #ff9800 0%, #ff5722 100%);
  border-color: #ff9800;
  color: white;
}

.ai-analysis-btn:hover {
  background: linear-gradient(135deg, #f57c00 0%, #e64a19 100%);
  border-color: #f57c00;
  color: white;
}

/* 活动卡片样式 */
.activities-card {
  position: sticky;
  top: 340px; /* 快速操作卡片高度 + 间距 */
  z-index: 9;
}

.charts-row {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 活动区域样式优化 */
.recent-activities {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.activity-item:hover {
  background-color: #f8f9fa;
}

.activity-avatar {
  margin-right: 12px;
  margin-top: 2px;
  flex-shrink: 0;
}

.activity-icon {
  font-size: 16px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.activity-icon.success {
  color: #67c23a;
  background: #f0f9eb;
}

.activity-icon.warning {
  color: #e6a23c;
  background: #fdf6ec;
}

.activity-icon.info {
  color: #409eff;
  background: #ecf5ff;
}

.activity-icon.primary {
  color: #909399;
  background: #f4f4f5;
}

.activity-icon.ai {
  color: #9c27b0;
  background: #f3e5f5;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-text {
  color: #606266;
  margin-bottom: 4px;
  line-height: 1.4;
  font-size: 13px;
}

.user-name {
  font-weight: 600;
  color: #303133;
  margin-right: 4px;
}

.action-text {
  color: #606266;
  margin-right: 4px;
}

.resource-name {
  color: #409eff;
  font-weight: 500;
  font-style: italic;
}

.activity-time {
  color: #909399;
  font-size: 11px;
}

.no-activities {
  text-align: center;
  padding: 20px 0;
}

.activities-footer {
  text-align: center;
  padding: 12px 0 4px;
  border-top: 1px solid #f0f0f0;
  margin-top: 8px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content-row {
    flex-direction: column;
  }

  .left-content,
  .right-content {
    width: 100%;
  }

  .quick-actions-card,
  .activities-card {
    position: static;
  }

  .quick-actions {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
  }

  .quick-action-btn {
    width: auto;
    min-width: 140px;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .quick-actions {
    flex-direction: column;
  }

  .quick-action-btn {
    width: 100%;
    justify-content: flex-start;
  }

  .activity-item {
    padding: 10px;
  }

  .activity-icon {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }

  .activity-text {
    font-size: 12px;
  }
}
</style>
