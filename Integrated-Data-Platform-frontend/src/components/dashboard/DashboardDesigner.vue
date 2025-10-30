<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/components/dashboard/DashboardDesigner.vue -->
<template>
  <div class="dashboard-designer">
    <div class="designer-header">
      <h3>看板布局设计 - {{ dashboard.name }}</h3>
      <div class="designer-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          保存布局
        </el-button>
      </div>
    </div>

    <div class="designer-content">
      <!-- 组件库 -->
      <div class="components-panel">
        <div class="panel-header">
          <h4>可视化组件</h4>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索组件..."
            size="small"
            clearable
          >
            <template #prefix>
              <el-icon>
                <Search/>
              </el-icon>
            </template>
          </el-input>
        </div>

        <div class="components-list">
          <div
            v-for="viz in filteredVisualizations"
            :key="viz.id"
            class="component-item"
            draggable="true"
            @dragstart="onDragStart(viz)"
          >
            <div class="component-icon">
              <el-icon>
                <component :is="getChartIcon(viz.chart_type_name)"/>
              </el-icon>
            </div>
            <div class="component-info">
              <div class="component-name">{{ viz.name }}</div>
              <div class="component-type">{{ viz.chart_type_name }}</div>
            </div>
          </div>

          <div v-if="filteredVisualizations.length === 0" class="no-components">
            <el-empty description="没有找到相关组件" :image-size="60"/>
          </div>
        </div>
      </div>

      <!-- 设计画布 -->
      <div class="design-canvas">
        <div class="canvas-header">
          <div class="canvas-tools">
            <el-button-group>
              <el-button size="small" @click="zoomOut">
                <el-icon>
                  <ZoomOut/>
                </el-icon>
              </el-button>
              <el-button size="small" @click="resetZoom">
                {{ Math.round(zoom * 100) }}%
              </el-button>
              <el-button size="small" @click="zoomIn">
                <el-icon>
                  <ZoomIn/>
                </el-icon>
              </el-button>
            </el-button-group>

            <el-button-group style="margin-left: 12px;">
              <el-button size="small" @click="clearCanvas">
                <el-icon>
                  <Delete/>
                </el-icon>
                清空
              </el-button>
              <el-button size="small" @click="autoLayout">
                <el-icon>
                  <SetUp/>
                </el-icon>
                自动布局
              </el-button>
            </el-button-group>
          </div>
        </div>

        <div
          class="canvas-area"
          @drop="onDrop"
          @dragover="onDragOver"
          :style="{ transform: `scale(${zoom})` }"
        >
          <div class="grid-background"></div>

          <!-- 布局组件 -->
          <div
            v-for="item in layoutItems"
            :key="item.id"
            class="layout-item"
            :class="{ 'map-layout-item': isMapChart(item) }"
            :style="getItemStyle(item)"
            @mousedown="startDrag(item, $event)"
          >
            <div class="item-header">
              <span class="item-title">{{ getVizName(item.visualization) }}</span>
              <div class="item-actions">
                <el-button
                  type="text"
                  size="small"
                  @click="removeItem(item)"
                >
                  <el-icon>
                    <Close/>
                  </el-icon>
                </el-button>
              </div>
            </div>
            <div class="item-preview" :class="{ 'map-preview': isMapChart(item) }">
              <el-icon class="preview-icon">
                <component :is="getChartIcon(getVizType(item.visualization))"/>
              </el-icon>
              <div v-if="isMapChart(item)" class="map-badge">地图</div>
            </div>

            <!-- 调整大小手柄 -->
            <div class="resize-handle" @mousedown="startResize(item, $event)"></div>
          </div>
        </div>
      </div>

      <!-- 属性面板 -->
      <div class="properties-panel">
        <div class="panel-header">
          <h4>组件属性</h4>
        </div>

        <div v-if="selectedItem" class="properties-form">
          <el-form label-width="80px">
            <el-form-item label="位置">
              <div class="position-controls">
                <el-input-number
                  v-model="selectedItem.position_x"
                  :min="0"
                  :max="11"
                  size="small"
                  controls-position="right"
                />
                <span style="margin: 0 8px;">X</span>
                <el-input-number
                  v-model="selectedItem.position_y"
                  :min="0"
                  :max="20"
                  size="small"
                  controls-position="right"
                />
                <span style="margin: 0 8px;">Y</span>
              </div>
            </el-form-item>

            <el-form-item label="大小">
              <div class="size-controls">
                <el-input-number
                  v-model="selectedItem.width"
                  :min="isMapChart(selectedItem) ? 4 : 2"
                  :max="12"
                  size="small"
                  controls-position="right"
                />
                <span style="margin: 0 8px;">W</span>
                <el-input-number
                  v-model="selectedItem.height"
                  :min="isMapChart(selectedItem) ? 4 : 2"
                  :max="8"
                  size="small"
                  controls-position="right"
                />
                <span style="margin: 0 8px;">H</span>
              </div>
            </el-form-item>

            <el-form-item label="组件信息">
              <div class="component-meta">
                <p><strong>名称:</strong> {{ getVizName(selectedItem.visualization) }}</p>
                <p><strong>类型:</strong> {{ getVizType(selectedItem.visualization) }}</p>
                <p v-if="isMapChart(selectedItem)" class="map-tip">
                  <el-icon><InfoFilled /></el-icon>
                  建议尺寸：最小 4x4，推荐 6x6
                </p>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <div v-else class="no-selection">
          <el-empty description="请选择画布中的组件" :image-size="60"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, computed, onMounted, watch} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {
  Search,
  ZoomIn,
  ZoomOut,
  Delete,
  SetUp,
  Close,
  InfoFilled
} from '@element-plus/icons-vue'

const props = defineProps({
  dashboard: Object,
  visualizations: Array,
  layoutData: Object
})

const emit = defineEmits(['save', 'cancel'])

const searchKeyword = ref('')
const zoom = ref(1)
const saving = ref(false)
const selectedItem = ref(null)
const draggingItem = ref(null)
const resizeItem = ref(null)
const isDragging = ref(false)
const dragOffset = ref({x: 0, y: 0})

const layoutItems = ref([])

// 计算属性
const filteredVisualizations = computed(() => {
  if (!searchKeyword.value) return props.visualizations
  const keyword = searchKeyword.value.toLowerCase()
  return props.visualizations.filter(viz =>
    viz.name.toLowerCase().includes(keyword) ||
    (viz.chart_type_name && viz.chart_type_name.toLowerCase().includes(keyword))
  )
})

// 🔥 新增：判断是否为地图组件
const isMapChart = (item) => {
  if (!item) return false
  const viz = props.visualizations.find(v => v.id === item.visualization)
  if (!viz) return false

  // 🔥 修复：确保 chart_type 是字符串类型
  const chartType = String(viz.chart_type_name || viz.chart_type || '')
  return chartType.includes('地图')
}

// 方法
const getChartIcon = (chartType) => {
  const iconMap = {
    '柱状图': 'Histogram',
    '折线图': 'TrendCharts',
    '饼图': 'PieChart',
    '散点图': 'ScatterPlot',
    '雷达图': 'DataBoard',
    '地图': 'MapLocation',
    '中国地图': 'MapLocation',
    '世界地图': 'MapLocation'
  }
  return iconMap[chartType] || 'DataAnalysis'
}

const getVizName = (vizId) => {
  const viz = props.visualizations.find(v => v.id === vizId)
  return viz?.name || '未知组件'
}

const getVizType = (vizId) => {
  const viz = props.visualizations.find(v => v.id === vizId)
  return viz?.chart_type_name || '未知类型'
}

const getItemStyle = (item) => {
  return {
    left: `${item.position_x * 100}px`,
    top: `${item.position_y * 80}px`,
    width: `${item.width * 100}px`,
    height: `${item.height * 80}px`
  }
}

const onDragStart = (viz) => {
  draggingItem.value = viz
}

const onDragOver = (e) => {
  e.preventDefault()
}

// 🔥 修复：拖放时自动为地图设置更大的尺寸
const onDrop = (e) => {
  e.preventDefault()
  if (!draggingItem.value) return

  const rect = e.currentTarget.getBoundingClientRect()
  const scale = zoom.value

  // 🔥 判断是否为地图组件并设置合适的尺寸
  const isMap = String(draggingItem.value.chart_type_name || '').includes('地图')
  const defaultWidth = isMap ? 6 : 4
  const defaultHeight = isMap ? 8 : 4  // 🔥 地图高度增加到8个单位

  const x = Math.floor((e.clientX - rect.left) / (100 * scale))
  const y = Math.floor((e.clientY - rect.top) / (80 * scale))

  // 检查位置是否被占用
  const isOccupied = layoutItems.value.some(item => {
    const itemRight = item.position_x + item.width
    const itemBottom = item.position_y + item.height
    return x < itemRight &&
      x + defaultWidth > item.position_x &&
      y < itemBottom &&
      y + defaultHeight > item.position_y
  })

  if (!isOccupied && x >= 0 && y >= 0 && x + defaultWidth <= 12) {
    layoutItems.value.push({
      id: Date.now() + Math.random(),
      visualization: draggingItem.value.id,
      position_x: x,
      position_y: y,
      width: defaultWidth,
      height: defaultHeight
    })
    ElMessage.success(`组件添加成功${isMap ? '（地图组件已自动设置为推荐尺寸）' : ''}`)
  } else {
    ElMessage.warning('该位置无法放置组件，请选择其他位置')
  }

  draggingItem.value = null
}

const startDrag = (item, e) => {
  selectedItem.value = item
  isDragging.value = true
  const rect = e.currentTarget.getBoundingClientRect()
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }

  const onMouseMove = (moveEvent) => {
    if (!isDragging.value) return

    const canvas = document.querySelector('.canvas-area')
    const canvasRect = canvas.getBoundingClientRect()
    const scale = zoom.value

    const newX = Math.floor((moveEvent.clientX - canvasRect.left - dragOffset.value.x) / (100 * scale))
    const newY = Math.floor((moveEvent.clientY - canvasRect.top - dragOffset.value.y) / (80 * scale))

    // 检查边界和碰撞
    if (newX >= 0 && newY >= 0 &&
      newX + item.width <= 12 &&
      !isPositionOccupied(item, newX, newY)) {
      item.position_x = newX
      item.position_y = newY
    }
  }

  const onMouseUp = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  e.preventDefault()
}

const isPositionOccupied = (currentItem, x, y) => {
  return layoutItems.value.some(item => {
    if (item.id === currentItem.id) return false
    const itemRight = item.position_x + item.width
    const itemBottom = item.position_y + item.height
    return x < itemRight &&
      x + currentItem.width > item.position_x &&
      y < itemBottom &&
      y + currentItem.height > item.position_y
  })
}

const startResize = (item, e) => {
  resizeItem.value = item
  const startWidth = item.width
  const startHeight = item.height
  const startX = e.clientX
  const startY = e.clientY

  const onMouseMove = (moveEvent) => {
    const deltaX = moveEvent.clientX - startX
    const deltaY = moveEvent.clientY - startY
    const scale = zoom.value

    // 🔥 为地图组件设置更大的最小尺寸
    const isMap = isMapChart(item)
    const minWidth = isMap ? 4 : 2
    const minHeight = isMap ? 6 : 2  // 🔥 地图最小高度6个单位

    const newWidth = Math.max(minWidth, Math.min(12, startWidth + Math.floor(deltaX / (100 * scale))))
    const newHeight = Math.max(minHeight, Math.min(12, startHeight + Math.floor(deltaY / (80 * scale))))

    // 检查边界
    if (item.position_x + newWidth <= 12) {
      item.width = newWidth
    }
    item.height = newHeight
  }

  const onMouseUp = () => {
    resizeItem.value = null
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  e.stopPropagation()
  e.preventDefault()
}

const removeItem = (item) => {
  const index = layoutItems.value.findIndex(i => i.id === item.id)
  if (index > -1) {
    layoutItems.value.splice(index, 1)
    ElMessage.success('组件已移除')
  }
  if (selectedItem.value === item) {
    selectedItem.value = null
  }
}

// 🔥 修复：加载布局数据时确保地图组件有合适的尺寸
const loadLayoutData = () => {
  console.log('🔄 加载布局数据 - 传入的layoutData:', props.layoutData)
  console.log('🔄 看板原始数据:', props.dashboard)

  // 重置布局项目
  layoutItems.value = []

  try {
    // 优先使用传入的layoutData
    if (props.layoutData && props.layoutData.items && Array.isArray(props.layoutData.items)) {
      console.log('✅ 使用传入的layoutData:', props.layoutData.items)
      layoutItems.value = props.layoutData.items.map(item => {
        // 🔥 查找对应的可视化组件信息
        const vizDetail = props.visualizations.find(v => v.id === item.visualization)
        const isMap = vizDetail && String(vizDetail.chart_type_name || '').includes('地图')

        // 🔥 如果是地图且高度太小，调整为合适的高度
        const width = isMap && item.width < 4 ? 6 : (item.width || 4)
        const height = isMap && item.height < 6 ? 8 : (item.height || 4) // 🔥 地图最小高度6，默认8

        return {
          id: item.id || Date.now() + Math.random(),
          visualization: item.visualization,
          position_x: Number(item.position_x) || 0,
          position_y: Number(item.position_y) || 0,
          width: Number(width),
          height: Number(height)
        }
      })

      // 设置缩放
      if (props.layoutData.layout_config && props.layoutData.layout_config.zoom) {
        zoom.value = props.layoutData.layout_config.zoom
      }
    }
    // 其他加载逻辑保持不变...
  } catch (error) {
    console.error('加载布局数据失败:', error)
    layoutItems.value = []
  }

  console.log('📦 最终布局项目:', layoutItems.value)
}

const zoomIn = () => {
  zoom.value = Math.min(zoom.value + 0.1, 2)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value - 0.1, 0.5)
}

const resetZoom = () => {
  zoom.value = 1
}

const clearCanvas = () => {
  ElMessageBox.confirm('确定要清空所有组件吗？此操作不可恢复。', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(() => {
    layoutItems.value = []
    selectedItem.value = null
    ElMessage.success('画布已清空')
  }).catch(() => {
  })
}

const autoLayout = () => {
  if (layoutItems.value.length === 0) {
    ElMessage.info('没有需要布局的组件')
    return
  }

  // 🔥 改进的自动布局算法，考虑地图组件
  const cols = 3
  layoutItems.value.forEach((item, index) => {
    const isMap = isMapChart(item)
    const row = Math.floor(index / cols)
    const col = index % cols

    // 🔥 为地图组件设置更大的默认尺寸
    if (isMap) {
      item.position_x = col * 4
      item.position_y = row * 6
      item.width = 4
      item.height = 6
    } else {
      item.position_x = col * 4
      item.position_y = row * 4
      item.width = 4
      item.height = 4
    }
  })

  ElMessage.success('自动布局完成')
}

const handleSave = async () => {
  if (layoutItems.value.length === 0) {
    ElMessage.warning('请至少添加一个组件到画布')
    return
  }

  saving.value = true
  try {
    const layoutData = {
      layout_config: {
        zoom: zoom.value,
        columns: 12,
        rowHeight: 80,
        template: 'custom'
      },
      items: layoutItems.value.map(item => ({
        visualization: item.visualization,
        position_x: item.position_x,
        position_y: item.position_y,
        width: item.width,
        height: item.height
      }))
    }

    console.log('💾 设计器保存数据:', layoutData)
    emit('save', layoutData)

  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleCancel = () => {
  console.log('❌ 取消布局设计')
  emit('cancel')
}

// 监听 layoutData 变化
watch(() => props.layoutData, () => {
  console.log('🔄 layoutData 发生变化，重新加载布局')
  loadLayoutData()
}, { immediate: true, deep: true })

// 监听 dashboard 变化
watch(() => props.dashboard, () => {
  console.log('🔄 dashboard 发生变化，重新加载布局')
  loadLayoutData()
}, { deep: true })

// 初始化
onMounted(() => {
  console.log('🎨 设计器初始化完成')
  loadLayoutData()
})
</script>

<style scoped>
.dashboard-designer {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.designer-header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.designer-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.designer-content {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 1px;
  background: #e8e8e8;
  overflow: hidden;
}

.components-panel,
.properties-panel {
  background: white;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  background: #fafafa;
}

.panel-header h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
}

.components-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.no-components {
  padding: 20px;
  text-align: center;
}

.component-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  cursor: move;
  background: white;
  transition: all 0.2s ease;
  user-select: none;
}

.component-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
}

.component-item:active {
  transform: translateY(0);
}

.component-icon {
  margin-right: 12px;
  color: #409EFF;
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.component-info {
  flex: 1;
}

.component-name {
  font-weight: 500;
  margin-bottom: 4px;
  font-size: 14px;
}

.component-type {
  font-size: 12px;
  color: #909399;
}

.design-canvas {
  background: white;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.canvas-header {
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  background: white;
  flex-shrink: 0;
}

.canvas-area {
  flex: 1;
  position: relative;
  overflow: auto;
  padding: 20px;
  transform-origin: 0 0;
  transition: transform 0.2s ease;
  min-height: 0;
}

.grid-background {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  background-image: linear-gradient(#e8e8e8 1px, transparent 1px),
  linear-gradient(90deg, #e8e8e8 1px, transparent 1px);
  background-size: 100px 80px;
  opacity: 0.3;
  pointer-events: none;
}

.layout-item {
  position: absolute;
  background: white;
  border: 2px solid #409EFF;
  border-radius: 6px;
  cursor: move;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  user-select: none;
  overflow: hidden;
  min-width: 200px;
  min-height: 160px;
}

.layout-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #67a8ff;
}

.layout-item.selected {
  border-color: #ff6b6b;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.2);
}

/* 🔥 地图布局项的特殊样式 */
.layout-item.map-layout-item {
  border-color: #67c23a;
  background: #f0f9ff;
  min-width: 400px;
  min-height: 320px;
}

.layout-item.map-layout-item:hover {
  border-color: #85ce61;
}

.layout-item.map-layout-item.selected {
  border-color: #f56c6c;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f0f9ff;
  border-bottom: 1px solid #e8e8e8;
  font-size: 12px;
}

.layout-item.map-layout-item .item-header {
  background: #e1f3d8;
}

.item-title {
  font-weight: 500;
  color: #409EFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.layout-item.map-layout-item .item-title {
  color: #67c23a;
}

.item-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.item-preview {
  height: calc(100% - 40px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  position: relative;
}

.layout-item.map-layout-item .item-preview {
  background: #f0f9ff;
}

.preview-icon {
  font-size: 32px;
  color: #c0c4cc;
}

.layout-item.map-layout-item .preview-icon {
  color: #67c23a;
  font-size: 48px;
}

/* 🔥 地图标识 */
.map-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: #67c23a;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.resize-handle {
  position: absolute;
  right: -4px;
  bottom: -4px;
  width: 12px;
  height: 12px;
  background: #409EFF;
  border-radius: 2px;
  cursor: nwse-resize;
  border: 2px solid white;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.2);
}

.resize-handle:hover {
  background: #67a8ff;
  transform: scale(1.1);
}

.layout-item.map-layout-item .resize-handle {
  background: #67c23a;
}

.layout-item.map-layout-item .resize-handle:hover {
  background: #85ce61;
}

.properties-form {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

.position-controls,
.size-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.component-meta {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 14px;
}

.component-meta p {
  margin: 4px 0;
}

.map-tip {
  background: #e1f3d8;
  padding: 8px;
  border-radius: 4px;
  border-left: 4px solid #67c23a;
  margin-top: 8px;
  font-size: 12px;
  color: #67c23a;
}

.map-tip .el-icon {
  margin-right: 4px;
}

.no-selection {
  padding: 40px 20px;
  text-align: center;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.layout-item.map-layout-item {
  border-color: #67c23a;
  background: #f0f9ff;
  min-width: 400px;
  min-height: 480px; /* 🔥 增加设计器中地图的最小高度 */
}
/* 响应式设计 */
@media (max-width: 1200px) {
  .designer-content {
    grid-template-columns: 250px 1fr;
  }

  .properties-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .designer-content {
    grid-template-columns: 1fr;
  }

  .components-panel {
    display: none;
  }

  .designer-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .designer-actions {
    display: flex;
    gap: 8px;
  }

  .layout-item {
    min-width: 150px;
    min-height: 120px;
  }

  .layout-item.map-layout-item {
    min-width: 300px;
    min-height: 240px;
  }
}

/* 滚动条样式 */
.components-list::-webkit-scrollbar,
.properties-form::-webkit-scrollbar,
.canvas-area::-webkit-scrollbar {
  width: 6px;
}

.components-list::-webkit-scrollbar-track,
.properties-form::-webkit-scrollbar-track,
.canvas-area::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.components-list::-webkit-scrollbar-thumb,
.properties-form::-webkit-scrollbar-thumb,
.canvas-area::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.components-list::-webkit-scrollbar-thumb:hover,
.properties-form::-webkit-scrollbar-thumb:hover,
.canvas-area::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
