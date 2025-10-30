<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/pages/Dashboards.vue -->
<template>
  <div class="dashboards-page">
    <div class="page-header">
      <h2>数据看板管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon>
          <Plus/>
        </el-icon>
        新建看板
      </el-button>
    </div>

    <!-- 看板列表 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated/>
    </div>

    <div v-else-if="dashboards.length === 0" class="empty-state">
      <el-empty description="暂无看板数据">
        <el-button type="primary" @click="showCreateDialog = true">创建第一个看板</el-button>
      </el-empty>
    </div>

    <el-row v-else :gutter="20">
      <el-col
        v-for="dashboard in dashboards"
        :key="dashboard.id"
        :xs="24" :sm="12" :md="8"
        class="dashboard-col"
      >
        <el-card class="dashboard-card" shadow="hover">
          <template #header>
            <div class="dashboard-header">
              <span class="dashboard-name">{{ dashboard.name }}</span>
              <div class="dashboard-actions">
                <el-button
                  type="primary"
                  size="small"
                  text
                  @click="viewDashboard(dashboard)"
                >
                  查看
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  text
                  @click="deleteDashboard(dashboard)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </template>

          <div class="dashboard-content">
            <p class="dashboard-description">
              {{ dashboard.description || '暂无描述' }}
            </p>

            <div class="dashboard-stats">
              <div class="stat">
                <el-icon>
                  <TrendCharts/>
                </el-icon>
                <span>{{ getVisualizationCount(dashboard) }} 个可视化</span>
              </div>
              <div class="stat">
                <el-icon>
                  <User/>
                </el-icon>
                <span>{{ dashboard.created_by || '系统用户' }}</span>
              </div>
            </div>

            <div class="dashboard-visualizations">
              <div
                v-for="item in getVisualizationPreviews(dashboard)"
                :key="item.id"
                class="visualization-preview"
              >
                <el-icon>
                  <DataAnalysis/>
                </el-icon>
                <span>{{ item.visualization_name || item.name }}</span>
              </div>
              <div
                v-if="getVisualizationCount(dashboard) > 3"
                class="visualization-more"
              >
                +{{ getVisualizationCount(dashboard) - 3 }} 更多
              </div>
            </div>
          </div>

          <div class="dashboard-footer">
            <span class="create-time">
              创建于 {{ formatDate(dashboard.created_at) }}
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建看板对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑看板' : '新建看板'"
      width="800px"
      @close="handleCreateClose"
    >
      <el-form
        :model="createForm"
        :rules="createRules"
        ref="createFormRef"
        label-width="100px"
      >
        <el-form-item label="看板名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入看板名称"/>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入看板描述"
          />
        </el-form-item>

        <el-form-item label="布局模板">
          <el-radio-group v-model="createForm.layout_template">
            <el-radio-button label="grid">网格布局</el-radio-button>
            <el-radio-button label="free">自由布局</el-radio-button>
            <el-radio-button label="report">报表布局</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="可视化组件">
          <div class="visualization-selection">
            <div class="selection-header">
              <span>选择可视化组件 (已选择 {{ selectedVisualizations.length }} 个)</span>
              <el-button type="text" @click="selectAllVisualizations">
                {{ isAllSelected ? '取消全选' : '全选' }}
              </el-button>
            </div>

            <div class="visualization-grid">
              <div
                v-for="viz in availableVisualizations"
                :key="viz.id"
                :class="['viz-item', { selected: isVizSelected(viz.id) }]"
                @click="toggleVisualization(viz.id)"
              >
                <div class="viz-icon">
                  <el-icon>
                    <component :is="getChartIcon(viz.chart_type_name)"/>
                  </el-icon>
                </div>
                <div class="viz-info">
                  <div class="viz-name">{{ viz.name }}</div>
                  <div class="viz-type">{{ viz.chart_type_name }}</div>
                </div>
                <div class="viz-check">
                  <el-icon v-if="isVizSelected(viz.id)" color="#409EFF">
                    <Check/>
                  </el-icon>
                </div>
              </div>
            </div>

            <div v-if="availableVisualizations.length === 0" class="no-visualizations">
              <el-empty description="暂无可视化组件" :image-size="80">
                <el-button type="primary" @click="$router.push('/visualization')">
                  去创建可视化
                </el-button>
              </el-empty>
            </div>
          </div>
        </el-form-item>

        <!-- 布局预览 -->
        <el-form-item v-if="selectedVisualizations.length > 0" label="布局预览">
          <div class="layout-preview">
            <div class="preview-grid">
              <div
                v-for="(viz, index) in selectedVisualizations"
                :key="viz.id"
                class="preview-item"
                :style="getPreviewItemStyle(index)"
              >
                <div class="preview-content">
                  <el-icon class="preview-icon">
                    <component :is="getChartIcon(viz.chart_type_name)"/>
                  </el-icon>
                  <span class="preview-name">{{ viz.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看看板对话框 -->
    <el-dialog
      v-model="showViewDialog"
      :title="currentDashboard?.name"
      width="95%"
      top="2vh"
      fullscreen
      class="dashboard-view-dialog"
      @close="handleViewDialogClose"
    >
      <div v-if="dashboardData" class="dashboard-view">
        <div class="dashboard-view-header">
          <div class="header-content">
            <h2>{{ currentDashboard?.name }}</h2>
            <p v-if="currentDashboard?.description" class="dashboard-description">
              {{ currentDashboard.description }}
            </p>
            <div class="dashboard-meta">
              <el-tag type="info">
                {{ getVisualizationCount(currentDashboard) }} 个可视化组件
              </el-tag>
              <el-tag type="success">
                创建时间: {{ formatDate(currentDashboard.created_at) }}
              </el-tag>
            </div>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="openLayoutDesigner">
              <el-icon>
                <Edit/>
              </el-icon>
              编辑布局
            </el-button>
            <el-button @click="exportDashboard">导出</el-button>
            <!-- 🔥 添加调试按钮 -->
            <el-button @click="debugCurrentDashboard" type="warning">
              <el-icon>
                <Search/>
              </el-icon>
              调试
            </el-button>
          </div>
        </div>

        <div class="dashboard-content-view">
          <div class="dashboard-grid-layout">
            <div
              v-for="viz in dashboardData.visualizations"
              :key="viz.id"
              class="dashboard-viz-item"
              :class="{ 'map-viz-item': isMapChart(viz) }"
              :style="getVizItemStyle(viz)"
            >
              <el-card class="viz-card" :class="{ 'map-viz-card': isMapChart(viz) }" shadow="hover">
                <template #header>
                  <div class="viz-header" :class="{ 'map-viz-header': isMapChart(viz) }">
                    <span class="viz-title">{{ viz.name }}</span>
                    <div class="viz-actions">
                      <el-tag size="small" :type="isMapChart(viz) ? 'success' : 'info'">
                        {{ viz.chart_type || viz.chart_type_name }}
                      </el-tag>
                      <el-button
                        type="text"
                        size="small"
                        @click="refreshVizData(viz)"
                        :loading="viz.loading"
                      >
                        <el-icon>
                          <Refresh/>
                        </el-icon>
                      </el-button>
                    </div>
                  </div>
                </template>
                <div class="viz-content">
                  <div class="chart-container" :class="{ 'map-chart-container': isMapChart(viz) }">
                    <component
                      :is="getChartComponent(viz.chart_type || viz.chart_type_name)"
                      :data="viz.chartData || viz.data"
                      :config="viz.config"
                      v-if="viz.chartData || viz.data"
                    />
                    <div v-else-if="viz.loading" class="loading-state">
                      <el-icon class="is-loading" color="#409EFF">
                        <Loading/>
                      </el-icon>
                      <p>图表数据加载中...</p>
                    </div>
                    <div v-else class="no-data">
                      <el-empty description="暂无数据" :image-size="60"/>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="loading-container">
        <el-skeleton :rows="10" animated/>
      </div>

      <template #footer>
        <el-button @click="showViewDialog = false">关闭</el-button>
        <el-button type="primary" @click="openLayoutDesigner">
          编辑布局
        </el-button>
      </template>
    </el-dialog>

    <!-- 布局设计对话框 -->
    <el-dialog
      v-model="showLayoutDialog"
      :title="`布局设计 - ${currentDashboard?.name}`"
      width="95%"
      top="2vh"
      fullscreen
      class="layout-designer-dialog"
      @close="handleLayoutDialogClose"
    >
      <DashboardDesigner
        v-if="showLayoutDialog && currentDashboard"
        :dashboard="currentDashboard"
        :visualizations="availableVisualizations"
        :layout-data="getCurrentLayoutData()"
        @save="handleLayoutSave"
        @cancel="showLayoutDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive, computed, onMounted, nextTick} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'
import {visualizationAPI} from '../api/visualization'
import DashboardDesigner from '../components/dashboard/DashboardDesigner.vue'
import {
  Plus,
  User,
  DataAnalysis,
  TrendCharts,
  Check,
  Edit,
  Refresh,
  Loading,
  Search
} from '@element-plus/icons-vue'

// 导入图表组件
import BarChart from '../components/charts/BarChart.vue'
import LineChart from '../components/charts/LineChart.vue'
import PieChart from '../components/charts/PieChart.vue'
import ScatterChart from '../components/charts/ScatterChart.vue'
import RadarChart from '../components/charts/RadarChart.vue'
import MapChart from '../components/charts/MapChart.vue' // 🔥 确保导入地图组件

const router = useRouter()

const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const showLayoutDialog = ref(false)
const isEditing = ref(false)
const isEditingDashboard = ref(false)

const dashboards = ref([])
const availableVisualizations = ref([])
const currentDashboard = ref(null)
const dashboardData = ref(null)

const createFormRef = ref()

const createForm = reactive({
  id: null,
  name: '',
  description: '',
  layout_template: 'grid',
  layout_config: {},
  visualizations: []
})

const selectedVisualizations = ref([])

const isMapChart = (viz) => {
  if (!viz) return false

  // 🔥 修复：确保 chart_type 是字符串类型，不依赖 props
  const chartType = String(viz.chart_type || viz.chart_type_name || '')
  return chartType.includes('地图')
}
// 🔥 修复：使用 localStorage 持久化存储
const LOCAL_STORAGE_KEY = 'dashboard_layouts'

// 从 localStorage 读取数据
const loadLocalDashboardLayouts = () => {
  try {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch (error) {
    console.error('读取本地存储失败:', error)
    return {}
  }
}

// 保存数据到 localStorage
const saveLocalDashboardLayouts = (layouts) => {
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(layouts))
  } catch (error) {
    console.error('保存到本地存储失败:', error)
  }
}

// 初始化本地存储
const localDashboardLayouts = ref(loadLocalDashboardLayouts())

const createRules = {
  name: [
    {required: true, message: '请输入看板名称', trigger: 'blur'},
    {min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur'}
  ]
}

// 计算属性
const isAllSelected = computed(() => {
  return availableVisualizations.value.length > 0 &&
    selectedVisualizations.value.length === availableVisualizations.value.length
})

// 方法

const getCurrentLayoutData = () => {
  if (!currentDashboard.value) return null

  const dashboardId = currentDashboard.value.id
  const localLayout = localDashboardLayouts.value[dashboardId]

  console.log('📋 获取当前布局数据:', {
    dashboardId,
    localLayout,
    currentDashboard: currentDashboard.value
  })

  // 优先使用本地存储的布局数据
  if (localLayout && localLayout.items && localLayout.items.length > 0) {
    console.log('✅ 使用本地存储的布局数据')
    return {
      layout_config: localLayout.layout_config || {
        template: 'custom',
        columns: 12,
        rowHeight: 80
      },
      items: localLayout.items
    }
  }

  // 如果没有本地数据，尝试从dashboard数据中提取
  if (currentDashboard.value.items_detail && currentDashboard.value.items_detail.length > 0) {
    console.log('✅ 使用dashboard的items_detail数据')
    return {
      layout_config: currentDashboard.value.layout_config || {
        template: 'custom',
        columns: 12,
        rowHeight: 80
      },
      items: currentDashboard.value.items_detail.map(item => ({
        id: item.id || Date.now() + Math.random(),
        visualization: item.visualization || item.id,
        position_x: item.position_x || 0,
        position_y: item.position_y || 0,
        width: item.width || 4,
        height: item.height || 4
      }))
    }
  }

  if (currentDashboard.value.items && currentDashboard.value.items.length > 0) {
    console.log('✅ 使用dashboard的items数据')
    return {
      layout_config: currentDashboard.value.layout_config || {
        template: 'custom',
        columns: 12,
        rowHeight: 80
      },
      items: currentDashboard.value.items.map(item => ({
        id: item.id || Date.now() + Math.random(),
        visualization: item.visualization,
        position_x: item.position_x || 0,
        position_y: item.position_y || 0,
        width: item.width || 4,
        height: item.height || 4
      }))
    }
  }

  console.log('⚠️ 没有找到现有布局数据，返回空数据')
  return {
    layout_config: {
      template: 'custom',
      columns: 12,
      rowHeight: 80
    },
    items: []
  }
}

const getVisualizationPreviews = (dashboard) => {
  console.log('📋 获取可视化预览:', dashboard)

  let items = []

  // 🔥 优先使用本地存储的数据
  const localLayout = localDashboardLayouts.value[dashboard.id]
  if (localLayout && localLayout.items && localLayout.items.length > 0) {
    console.log('✅ 使用本地存储的布局数据')
    items = localLayout.items
  } else if (dashboard.items_detail && Array.isArray(dashboard.items_detail) && dashboard.items_detail.length > 0) {
    items = dashboard.items_detail
  } else {
    // 检查其他可能的数组字段
    const allFields = Object.keys(dashboard)
    for (const field of allFields) {
      if (Array.isArray(dashboard[field]) && dashboard[field].length > 0) {
        console.log(`✅ 使用字段 ${field} 的数据`)
        items = dashboard[field]
        break
      }
    }
  }

  console.log('📋 处理后的预览项目:', items)

  // 转换项目格式，确保有正确的显示名称
  const previewItems = items.map(item => {
    const viz = availableVisualizations.value.find(v => v.id === item.visualization)
    return {
      ...item,
      visualization_name: viz?.name || '未知组件',
      name: viz?.name || '未知组件'
    }
  })

  return previewItems.slice(0, 3)
}

const getChartIcon = (chartType) => {
  const iconMap = {
    '柱状图': 'Histogram',
    '折线图': 'TrendCharts',
    '饼图': 'PieChart',
    '散点图': 'ScatterPlot',
    '雷达图': 'DataBoard',
    '地图': 'MapLocation', // 🔥 添加地图图标
    '中国地图': 'MapLocation',
    '世界地图': 'MapLocation'
  }
  return iconMap[chartType] || 'DataAnalysis'
}

// 🔥 修复：更新图表组件映射，添加地图组件
const getChartComponent = (chartType) => {
  // 🔥 修复：确保输入是字符串
  const type = String(chartType || '柱状图')
  const componentMap = {
    '柱状图': BarChart,
    '折线图': LineChart,
    '饼图': PieChart,
    '散点图': ScatterChart,
    '雷达图': RadarChart,
    '地图': MapChart,
    '中国地图': MapChart,
    '世界地图': MapChart
  }
  return componentMap[type] || BarChart
}

const isVizSelected = (vizId) => {
  return selectedVisualizations.value.some(viz => viz.id === vizId)
}

const toggleVisualization = (vizId) => {
  const viz = availableVisualizations.value.find(v => v.id === vizId)
  if (!viz) return

  const index = selectedVisualizations.value.findIndex(v => v.id === vizId)
  if (index > -1) {
    selectedVisualizations.value.splice(index, 1)
  } else {
    selectedVisualizations.value.push(viz)
  }
}

const selectAllVisualizations = () => {
  if (isAllSelected.value) {
    selectedVisualizations.value = []
  } else {
    selectedVisualizations.value = [...availableVisualizations.value]
  }
}

const getPreviewItemStyle = (index) => {
  const row = Math.floor(index / 3)
  const col = index % 3
  return {
    gridColumn: `${col + 1} / span 1`,
    gridRow: `${row + 1} / span 1`
  }
}

const getVizItemStyle = (viz) => {
  if (!viz) {
    return {
      gridColumn: '1 / span 4',
      gridRow: '1 / span 4'
    }
  }

  let position = {x: 0, y: 0, w: 4, h: 4}

  // 🔥 安全地检查是否为地图
  const isMap = isMapChart(viz)

  // 🔥 为地图设置更大的默认高度，确保地图有足够的显示空间
  const defaultWidth = isMap ? 6 : 4
  const defaultHeight = isMap ? 8 : 4  // 🔥 地图高度增加到8个单位

  if (viz.position) {
    position = {
      x: Number(viz.position.x) || 0,
      y: Number(viz.position.y) || 0,
      w: Number(viz.position.w) || defaultWidth,
      h: Number(viz.position.h) || defaultHeight
    }
  } else if (viz.position_x !== undefined && viz.position_y !== undefined) {
    position = {
      x: Number(viz.position_x) || 0,
      y: Number(viz.position_y) || 0,
      w: Number(viz.width) || defaultWidth,
      h: Number(viz.height) || defaultHeight
    }
  } else {
    // 如果没有位置信息，使用默认值
    position = {
      x: 0,
      y: 0,
      w: defaultWidth,
      h: defaultHeight
    }
  }

  // 🔥 确保值在合理范围内
  const x = Math.max(0, Math.min(11, position.x))
  const y = Math.max(0, position.y)
  const w = Math.max(isMap ? 4 : 2, Math.min(12, position.w))
  const h = Math.max(isMap ? 6 : 2, Math.min(12, position.h)) // 🔥 地图最小高度6个单位

  return {
    gridColumn: `${x + 1} / span ${w}`,
    gridRow: `${y + 1} / span ${h}`
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadDashboards = async () => {
  loading.value = true
  try {
    const response = await visualizationAPI.getDashboards()
    console.log('📊 看板原始数据:', response)

    dashboards.value = Array.isArray(response) ? response : []
    console.log('✅ 处理后的看板数据:', dashboards.value)

    // 🔥 修复：初始化本地存储（从 localStorage 读取）
    const currentLayouts = {...localDashboardLayouts.value}

    dashboards.value.forEach(dashboard => {
      if (!currentLayouts[dashboard.id]) {
        // 如果有后端数据，初始化本地存储
        if (dashboard.items_detail && dashboard.items_detail.length > 0) {
          currentLayouts[dashboard.id] = {
            layout_config: dashboard.layout_config || {},
            items: dashboard.items_detail
          }
        } else {
          // 否则创建空的本地存储
          currentLayouts[dashboard.id] = {
            layout_config: dashboard.layout_config || {},
            items: []
          }
        }
      }
    })

    // 🔥 更新本地存储
    localDashboardLayouts.value = currentLayouts
    saveLocalDashboardLayouts(currentLayouts)

    console.log('💾 本地存储数据:', localDashboardLayouts.value)

  } catch (error) {
    console.error('加载看板失败:', error)
    ElMessage.error('加载看板失败')
    dashboards.value = []
  } finally {
    loading.value = false
  }
}
const getVisualizationCount = (dashboard) => {
  console.log('🔢 计算可视化数量 - 完整看板数据:', dashboard);

  // 🔥 优先检查本地存储的数据
  const localLayout = localDashboardLayouts.value[dashboard.id]
  if (localLayout && localLayout.items && localLayout.items.length > 0) {
    console.log('✅ 使用本地存储的布局数据:', localLayout.items.length)
    return localLayout.items.length
  }

  // 检查所有可能的字段
  const countFields = [
    'charts_count',
    'chart_count',
    'visualization_count',
    'visualizations_count',
    'viz_count'
  ];

  for (const field of countFields) {
    if (dashboard[field] !== undefined && dashboard[field] !== null) {
      console.log(`✅ 找到数量字段 ${field}:`, dashboard[field]);
      return dashboard[field];
    }
  }

  // 然后检查后端返回的数据
  if (dashboard.items_detail && Array.isArray(dashboard.items_detail) && dashboard.items_detail.length > 0) {
    console.log('✅ 使用 items_detail 长度:', dashboard.items_detail.length);
    return dashboard.items_detail.length
  }

  // 检查其他数组字段
  const allFields = Object.keys(dashboard)
  for (const field of allFields) {
    if (Array.isArray(dashboard[field]) && dashboard[field].length > 0) {
      console.log(`✅ 在字段 ${field} 中找到数据:`, dashboard[field].length)
      return dashboard[field].length
    }
  }

  console.log('❌ 所有数据源都为空，返回0');
  return 0
}
const loadVisualizations = async () => {
  try {
    const response = await visualizationAPI.getVisualizations()
    console.log('📈 可视化原始数据:', response)

    availableVisualizations.value = Array.isArray(response) ? response : []
    console.log('✅ 处理后的可视化数据:', availableVisualizations.value)

  } catch (error) {
    console.error('加载可视化组件失败:', error)
    ElMessage.error('加载可视化组件失败')
    availableVisualizations.value = []
  }
}

const handleCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      console.log('🔍 调试 - 选择的可视化组件:', selectedVisualizations.value)

      if (selectedVisualizations.value.length === 0) {
        ElMessage.warning('请至少选择一个可视化组件')
        return
      }

      creating.value = true
      try {
        const dashboardData = {
          name: createForm.name,
          description: createForm.description,
          layout_config: {
            template: createForm.layout_template,
            columns: 12,
            rowHeight: 100
          },
          items: selectedVisualizations.value.map((viz, index) => ({
            visualization: viz.id,
            position_x: (index % 3) * 4,
            position_y: Math.floor(index / 3) * 4,
            width: 4,
            height: 4
          }))
        }

        console.log('📤 创建看板数据:', dashboardData)

        let result
        if (isEditing.value && createForm.id) {
          result = await visualizationAPI.updateDashboard(createForm.id, dashboardData)
          console.log('✅ 更新看板响应:', result)
          ElMessage.success('更新成功')
        } else {
          result = await visualizationAPI.createDashboard(dashboardData)
          console.log('✅ 创建看板响应:', result)
          ElMessage.success('创建成功')

          // 🔥 修复：创建成功后立即在本地存储布局数据
          if (result && result.id) {
            localDashboardLayouts.value[result.id] = {
              layout_config: dashboardData.layout_config,
              items: dashboardData.items
            }
            // 🔥 保存到 localStorage
            saveLocalDashboardLayouts(localDashboardLayouts.value)
            console.log('💾 已保存到本地存储:', localDashboardLayouts.value[result.id])
          }
        }

        showCreateDialog.value = false
        await loadDashboards()
      } catch (error) {
        console.error('❌ 操作失败:', error)
        console.error('❌ 错误详情:', error.response?.data)
        ElMessage.error(isEditing.value ? '更新失败' : '创建失败: ' + (error.message || '未知错误'))
      } finally {
        creating.value = false
      }
    }
  })
}

const handleCreateClose = () => {
  createFormRef.value?.resetFields()
  Object.assign(createForm, {
    id: null,
    name: '',
    description: '',
    layout_template: 'grid',
    layout_config: {},
    visualizations: []
  })
  selectedVisualizations.value = []
  isEditing.value = false
}

// 🔥 修复：新增对话框关闭处理方法
const handleViewDialogClose = () => {
  console.log('🔒 查看对话框关闭')
  // 如果正在编辑，不要重置数据
  if (!isEditingDashboard.value) {
    currentDashboard.value = null
    dashboardData.value = null
  }
}

const handleLayoutDialogClose = () => {
  console.log('🔒 布局对话框关闭')
  isEditingDashboard.value = false

  // 🔥 修复：如果查看对话框还开着，刷新数据
  if (showViewDialog.value && currentDashboard.value) {
    refreshDashboardView()
  }
}

// 🔥 修复：新增刷新看板视图方法
const refreshDashboardView = async () => {
  if (!currentDashboard.value) return

  try {
    console.log('🔄 刷新看板视图')

    // 🔥 修复：直接使用本地存储数据，不调用API
    dashboardData.value = {
      id: currentDashboard.value.id,
      name: currentDashboard.value.name,
      description: currentDashboard.value.description,
      visualizations: []
    }

    // 重新构建可视化
    const localLayout = localDashboardLayouts.value[currentDashboard.value.id]
    if (localLayout && localLayout.items && localLayout.items.length > 0) {
      await buildVisualizationsFromItems(localLayout.items)
    } else {
      // 如果没有本地数据，使用dashboard原始数据
      const dashboard = currentDashboard.value
      if (dashboard.items_detail && dashboard.items_detail.length > 0) {
        await buildVisualizationsFromItems(dashboard.items_detail)
      } else if (dashboard.items && dashboard.items.length > 0) {
        await buildVisualizationsFromItems(dashboard.items)
      }
    }
  } catch (error) {
    console.error('刷新看板数据失败:', error)
    ElMessage.error('刷新看板数据失败')
  }
}

// 🔥 修复：新增打开布局设计器方法
const openLayoutDesigner = () => {
  console.log('🎨 打开布局设计器')

  // 🔥 修复：直接打开布局对话框，不关闭查看对话框
  showLayoutDialog.value = true
  isEditingDashboard.value = true
}

// 🔥 修复：完全重写 viewDashboard 方法，移除有问题的API调用
const viewDashboard = async (dashboard) => {
  currentDashboard.value = dashboard
  showViewDialog.value = true
  dashboardData.value = null
  isEditingDashboard.value = false

  try {
    console.log('🔍 查看看板:', dashboard)

    // 🔥 修复：直接创建看板数据结构，不调用有问题的API
    dashboardData.value = {
      id: dashboard.id,
      name: dashboard.name,
      description: dashboard.description,
      visualizations: []
    }

    // 🔥 优先使用本地存储的数据构建可视化
    const localLayout = localDashboardLayouts.value[dashboard.id]
    if (localLayout && localLayout.items && localLayout.items.length > 0) {
      console.log('✅ 使用本地存储的布局数据构建可视化')
      await buildVisualizationsFromItems(localLayout.items)
    }
    // 如果没有本地数据，尝试从dashboard原始数据中构建
    else if (dashboard.items_detail && Array.isArray(dashboard.items_detail) && dashboard.items_detail.length > 0) {
      console.log('✅ 使用dashboard的items_detail数据构建可视化')
      await buildVisualizationsFromItems(dashboard.items_detail)
    } else if (dashboard.items && Array.isArray(dashboard.items) && dashboard.items.length > 0) {
      console.log('✅ 使用dashboard的items数据构建可视化')
      await buildVisualizationsFromItems(dashboard.items)
    } else {
      console.log('❌ 所有数据源都为空，显示空状态')
      dashboardData.value.visualizations = []
    }

  } catch (error) {
    console.error('加载看板数据失败:', error)
    ElMessage.error('加载看板数据失败: ' + (error.message || '未知错误'))
  }
}

// 🔥 修复：增强 buildVisualizationsFromItems 方法的容错性
const buildVisualizationsFromItems = async (items) => {
  console.log('🔄 从项目数据构建可视化:', items)

  if (!items || items.length === 0) {
    console.log('❌ 项目数据为空')
    if (dashboardData.value) {
      dashboardData.value.visualizations = []
    }
    return
  }

  const visualizations = []

  for (const item of items) {
    try {
      let vizDetail = null
      const vizId = item.visualization || item.id

      if (vizId) {
        vizDetail = availableVisualizations.value.find(v => v.id === vizId)
      }

      if (vizDetail) {
        // 🔥 修复：使用正确的 isMapChart 判断
        const isMap = isMapChart(vizDetail)

        // 🔥 为地图设置更大的默认尺寸
        const defaultWidth = isMap ? 6 : 4
        const defaultHeight = isMap ? 8 : 4

        const vizData = {
          ...vizDetail,
          id: item.id || vizDetail.id || Date.now() + Math.random(),
          position_x: Number(item.position_x) || 0,
          position_y: Number(item.position_y) || 0,
          width: Number(item.width) || defaultWidth,
          height: Number(item.height) || defaultHeight,
          loading: true,
          // 🔥 修复：确保 chart_type 和 chart_type_name 是字符串
          chart_type: String(vizDetail.chart_type_name || vizDetail.chart_type || '柱状图'),
          chart_type_name: String(vizDetail.chart_type_name || vizDetail.chart_type || '柱状图')
        }
        visualizations.push(vizData)

        // 异步加载图表数据
        await loadVizData(vizData)
      } else {
        console.warn('❌ 未找到可视化详情，创建占位符:', item.visualization)
        const placeholderViz = {
          id: item.id || Date.now() + Math.random(),
          name: `未知组件-${item.visualization || '未知'}`,
          position_x: Number(item.position_x) || 0,
          position_y: Number(item.position_y) || 0,
          width: Number(item.width) || 4,
          height: Number(item.height) || 4,
          loading: false,
          chart_type: '柱状图',
          chart_type_name: '柱状图',
          chartData: null,
          data: null
        }
        visualizations.push(placeholderViz)
      }
    } catch (error) {
      console.error(`构建可视化失败:`, error, '项目数据:', item)
      // 创建错误占位符
      const errorViz = {
        id: item.id || Date.now() + Math.random(),
        name: `错误组件-${item.visualization || '未知'}`,
        position_x: Number(item.position_x) || 0,
        position_y: Number(item.position_y) || 0,
        width: Number(item.width) || 4,
        height: Number(item.height) || 4,
        loading: false,
        chart_type: '柱状图',
        chart_type_name: '柱状图',
        chartData: null,
        data: null,
        error: error.message
      }
      visualizations.push(errorViz)
    }
  }

  if (dashboardData.value) {
    dashboardData.value.visualizations = visualizations
  }
  console.log('✅ 构建的可视化数据:', visualizations)
}

// 🔥 修复：增强 loadVizData 方法，特别处理地图数据
const loadVizData = async (viz) => {
  try {
    viz.loading = true
    console.log('📈 加载图表数据:', viz.id, viz.name, '图表类型:', viz.chart_type)

    // 🔥 修复：确保图表类型是字符串
    const chartType = String(viz.chart_type || viz.chart_type_name || '')
    const isMapChartType = chartType.includes('地图')

    // 🔥 修复：如果viz.id不存在或者是占位符，跳过数据加载
    if (!viz.id || viz.id.toString().includes('未知') || !viz.id.toString().match(/^\d+$/)) {
      console.log('⏭️ 跳过占位符组件的图表数据加载')
      viz.chartData = null
      viz.data = null
      return
    }

    console.log('🔄 调用API获取数据，可视化ID:', viz.id)
    const response = await visualizationAPI.getVisualizationData(viz.id)
    console.log('📊 图表数据完整响应:', response)

    // 🔥 修复：特别处理地图数据 - 直接传递正确的地图数据
    if (isMapChartType) {
      console.log('🗺️ 检测到地图图表，特殊处理数据格式')

      // 🔥 关键修复：直接使用 response.data.data 作为地图数据
      if (response && response.data && response.data.data && Array.isArray(response.data.data)) {
        viz.chartData = response.data.data
        console.log('✅ 使用 response.data.data 作为地图数据:', viz.chartData)
      } else {
        // 如果数据结构不对，尝试其他方式提取
        viz.chartData = processMapData(response)
        console.log('🔄 使用 processMapData 处理后的数据:', viz.chartData)
      }
    } else {
      // 处理普通图表数据格式
      if (response && response.data) {
        viz.chartData = response.data
        console.log('✅ 使用 response.data:', viz.chartData)
      } else if (response && response.categories && response.series) {
        viz.chartData = response
        console.log('✅ 使用标准图表数据格式:', viz.chartData)
      } else {
        viz.chartData = response
        console.log('✅ 使用完整响应作为图表数据:', viz.chartData)
      }
    }

    viz.data = response

    // 确保配置信息正确
    if (response && response.config) {
      viz.config = response.config
    } else if (viz.configuration) {
      viz.config = viz.configuration
    }

    // 🔥 修复：如果没有配置，为地图设置默认配置
    if (isMapChartType && !viz.config) {
      viz.config = {
        mapType: chartType === '世界地图' ? 'world' : 'china',
        roam: true,
        emphasis: {
          focus: 'self'
        }
      }
    }

    console.log('🎯 最终配置信息:', viz.config)
    console.log('🎯 最终图表数据:', viz.chartData)

  } catch (error) {
    console.error(`加载图表数据失败 (${viz.name}):`, error)
    viz.chartData = null
    viz.data = null
  } finally {
    viz.loading = false
  }
}

// 🔥 新增：处理地图数据的函数
const processMapData = (response) => {
  console.log('🗺️ 处理地图数据:', response)

  if (!response) return null

  // 如果响应中已经有标准的地图数据格式，直接使用
  if (response.data && Array.isArray(response.data)) {
    return response.data
  }

  // 如果响应本身就是数组格式，直接使用
  if (Array.isArray(response)) {
    return response
  }

  // 尝试从响应中提取地图数据
  if (response.series && Array.isArray(response.series)) {
    return response.series
  }

  // 如果是对象格式，转换为数组
  if (typeof response === 'object' && !Array.isArray(response)) {
    const dataArray = []
    for (const [name, value] of Object.entries(response)) {
      if (name !== 'config' && name !== 'categories' && name !== 'series') {
        dataArray.push({
          name: name,
          value: typeof value === 'number' ? value : 0
        })
      }
    }
    return dataArray.length > 0 ? dataArray : null
  }

  return response
}

const refreshVizData = async (viz) => {
  await loadVizData(viz)
  ElMessage.success('数据已刷新')
}

const editDashboard = (dashboard) => {
  console.log('📝 编辑看板:', dashboard)
  currentDashboard.value = dashboard
  showViewDialog.value = false

  // 🔥 修复：使用 nextTick 确保 DOM 更新后再打开布局对话框
  nextTick(() => {
    showLayoutDialog.value = true
    isEditingDashboard.value = true
  })
}

const handleLayoutSave = async (newLayout) => {
  try {
    console.log('💾 保存布局数据:', newLayout)

    const updateData = {
      layout_config: newLayout.layout_config,
      items: newLayout.items.map(item => ({
        visualization: item.visualization,
        position_x: item.position_x,
        position_y: item.position_y,
        width: item.width,
        height: item.height
      }))
    }

    console.log('📤 更新看板数据:', updateData)

    // 🔥 关键修复：先更新本地存储，再调用API
    if (currentDashboard.value) {
      localDashboardLayouts.value[currentDashboard.value.id] = {
        layout_config: newLayout.layout_config,
        items: newLayout.items
      }
      // 🔥 保存到 localStorage
      saveLocalDashboardLayouts(localDashboardLayouts.value)
      console.log('✅ 本地存储已更新并保存:', localDashboardLayouts.value[currentDashboard.value.id])
    }

    // 仍然调用API，但不再依赖它的响应
    await visualizationAPI.updateDashboard(currentDashboard.value.id, updateData)
    ElMessage.success('布局保存成功')
    showLayoutDialog.value = false
    isEditingDashboard.value = false

    // 重新加载数据（会使用本地存储的数据）
    await loadDashboards()

    // 🔥 修复：确保重新打开查看对话框
    await nextTick()
    if (currentDashboard.value) {
      await viewDashboard(currentDashboard.value)
      showViewDialog.value = true
    }

  } catch (error) {
    console.error('保存布局失败:', error)
    ElMessage.error('保存布局失败: ' + (error.message || '未知错误'))
  }
}

const deleteDashboard = async (dashboard) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除看板 "${dashboard.name}" 吗？此操作不可恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await visualizationAPI.deleteDashboard(dashboard.id)

    // 🔥 同时删除本地存储
    if (localDashboardLayouts.value[dashboard.id]) {
      delete localDashboardLayouts.value[dashboard.id]
      // 🔥 保存到 localStorage
      saveLocalDashboardLayouts(localDashboardLayouts.value)
    }

    ElMessage.success('删除成功')
    await loadDashboards()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const exportDashboard = () => {
  ElMessage.info('导出功能开发中...')
}

// 🔥 新增：调试函数
const debugCurrentDashboard = () => {
  console.group('🔍 当前看板调试信息')
  console.log('当前看板:', currentDashboard.value)
  console.log('看板数据:', dashboardData.value)
  console.log('本地存储数据:', localDashboardLayouts.value[currentDashboard.value?.id])

  if (dashboardData.value && dashboardData.value.visualizations) {
    console.log('可视化组件列表:')
    dashboardData.value.visualizations.forEach((viz, index) => {
      console.group(`可视化组件 ${index + 1}: ${viz.name}`)
      console.log('ID:', viz.id)
      console.log('图表类型:', viz.chart_type)
      console.log('是否有数据:', !!(viz.chartData || viz.data))
      console.log('图表数据:', viz.chartData)
      console.log('原始数据:', viz.data)
      console.log('配置:', viz.config)
      console.log('是否地图类型:', viz.chart_type?.includes('地图') || viz.chart_type_name?.includes('地图'))
      console.groupEnd()
    })
  }
  console.groupEnd()

  ElMessage.info('调试信息已输出到控制台')
}

onMounted(() => {
  loadDashboards()
  loadVisualizations()
})
</script>

<style scoped>
.dashboards-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #409EFF;
}

.loading-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: rotating 2s linear infinite;
}

.loading-state p {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-col {
  margin-bottom: 20px;
}

.dashboard-card {
  height: 320px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-name {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.dashboard-actions {
  display: flex;
  gap: 4px;
}

.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.dashboard-description {
  color: #606266;
  margin-bottom: 16px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dashboard-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.dashboard-stats .stat {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.dashboard-visualizations {
  flex: 1;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 12px;
  background: #fafafa;
}

.visualization-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #e8e8e8;
  color: #333;
  font-size: 14px;
}

.visualization-preview:last-child {
  border-bottom: none;
}

.visualization-more {
  padding: 8px 0;
  color: #909399;
  font-style: italic;
  text-align: center;
}

.dashboard-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
  margin-top: 12px;
}

.create-time {
  color: #909399;
  font-size: 12px;
}

/* 可视化选择样式 */
.visualization-selection {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
}

.visualization-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.viz-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 2px solid #f0f0f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.viz-item:hover {
  border-color: #c0c4cc;
}

.viz-item.selected {
  border-color: #409EFF;
  background: #f0f9ff;
}

.viz-icon {
  margin-right: 12px;
  color: #409EFF;
}

.viz-info {
  flex: 1;
}

.viz-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.viz-type {
  font-size: 12px;
  color: #909399;
}

.viz-check {
  margin-left: 8px;
}

.no-visualizations {
  text-align: center;
  padding: 20px;
}

/* 布局预览 */
.layout-preview {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 80px);
  gap: 8px;
}

.preview-item {
  background: white;
  border: 1px dashed #c0c4cc;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-content {
  text-align: center;
}

.preview-icon {
  font-size: 20px;
  color: #409EFF;
  margin-bottom: 4px;
}

.preview-name {
  font-size: 12px;
  color: #606266;
  display: block;
}

/* 看板查看样式 */
.dashboard-view-dialog {
  .el-dialog__body {
    padding: 0;
    background: #f8fafc;
  }
}

.dashboard-view {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}

.dashboard-view-header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-content {
  flex: 1;
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 24px;
  font-weight: 700;
}

.dashboard-meta {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.dashboard-content-view {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.dashboard-grid-layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
  align-content: start;
}

.dashboard-viz-item {
  min-height: 200px;
}

.viz-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.viz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.viz-title {
  font-weight: 500;
}

.viz-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.viz-content {
  flex: 1;
  padding: 0;
}

.chart-container {
  height: 100%;
  width: 100%;
  min-height: 200px;
}

.no-data {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-container, .empty-state {
  margin: 40px 0;
}

.dashboard-grid-layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
  align-content: start;
  min-height: 800px; /* 🔥 增加整体最小高度 */
  padding: 20px;
}

.dashboard-viz-item {
  min-height: 200px;
  transition: all 0.3s ease;
}

/* 🔥 为地图图表项设置更大的最小高度 */
.dashboard-viz-item.map-viz-item {
  min-height: 500px !important; /* 🔥 大幅增加地图最小高度 */
}

.viz-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

/* 🔥 地图卡片特殊样式 */
.viz-card.map-viz-card {
  border: 2px solid #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
}

.viz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

/* 🔥 地图头部特殊样式 */
.viz-header.map-viz-header {
  background: linear-gradient(135deg, #e1f3d8 0%, #d1edc4 100%);
  border-bottom: 2px solid #67c23a;
}

.viz-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.viz-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.viz-content {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
  min-height: 300px; /* 🔥 确保内容区域有足够高度 */
}

.chart-container {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 150px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

/* 🔥 修复：大幅改进地图图表容器的样式 */
.chart-container.map-chart-container {
  min-height: 400px !important; /* 🔥 大幅增加地图最小高度 */
  height: 100% !important;
  padding: 0;
  background: #ffffff;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

/* 🔥 确保地图组件填满整个容器 */
.chart-container.map-chart-container ::v-deep(.map-chart-container) {
  width: 100% !important;
  height: 100% !important;
  min-height: 400px !important;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #409EFF;
  min-height: 200px;
}

.loading-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: rotating 2s linear infinite;
}

.loading-state p {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
}

.no-data {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-col {
    margin-bottom: 16px;
  }

  .dashboard-card {
    height: auto;
    min-height: 280px;
  }

  .visualization-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-view-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .dashboard-grid-layout {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 10px;
  }

  .dashboard-viz-item {
    min-height: 300px;
  }

  .dashboard-viz-item.map-viz-item {
    min-height: 400px !important;
  }

  .chart-container.map-chart-container {
    min-height: 350px !important;
  }
}

@media (min-width: 1200px) {
  .dashboard-viz-item.map-viz-item {
    min-height: 600px !important;
  }

  .chart-container.map-chart-container {
    min-height: 500px !important;
  }
}

/* 🔥 确保网格项有足够的空间 */
.dashboard-viz-item {
  grid-row: span 4; /* 默认高度 */
}

.dashboard-viz-item.map-viz-item {
  grid-row: span 8 !important; /* 🔥 地图使用更多行空间 */
}
</style>
