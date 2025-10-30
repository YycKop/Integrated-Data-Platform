<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/common/DataTable.vue-->
<template>
  <div class="data-table-container">
    <!-- 表格工具栏 -->
    <div class="table-toolbar" v-if="showToolbar">
      <div class="toolbar-left">
        <slot name="toolbar-left">
          <el-button
            v-if="showRefresh"
            @click="handleRefresh"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>

          <el-button
            v-if="showExport && data.length > 0"
            @click="handleExport"
          >
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </slot>
      </div>

      <div class="toolbar-right">
        <slot name="toolbar-right">
          <el-input
            v-if="showSearch"
            v-model="searchText"
            placeholder="搜索..."
            prefix-icon="Search"
            style="width: 200px"
            clearable
            @input="handleSearch"
          />

          <el-button
            v-if="showColumnSelector"
            @click="showColumnDialog = true"
          >
            <el-icon><Setting /></el-icon>
            列设置
          </el-button>
        </slot>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      ref="tableRef"
      :data="filteredData"
      :border="border"
      :stripe="stripe"
      :size="size"
      :height="height"
      :max-height="maxHeight"
      :highlight-current-row="highlightCurrentRow"
      :row-class-name="rowClassName"
      :cell-class-name="cellClassName"
      v-loading="loading"
      :empty-text="emptyText"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
      @sort-change="handleSortChange"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
        align="center"
      />

      <!-- 序号列 -->
      <el-table-column
        v-if="showIndex"
        type="index"
        label="序号"
        width="80"
        align="center"
        :index="indexMethod"
      />

      <!-- 数据列 -->
      <template v-for="column in visibleColumns" :key="column.prop">
        <el-table-column
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
          :min-width="column.minWidth"
          :align="column.align || 'left'"
          :sortable="column.sortable"
          :fixed="column.fixed"
          :show-overflow-tooltip="column.showOverflowTooltip !== false"
        >
          <template #default="scope">
            <slot
              :name="`column-${column.prop}`"
              :row="scope.row"
              :$index="scope.$index"
            >
              <!-- 格式化显示 -->
              <template v-if="column.formatter">
                {{ column.formatter(scope.row[column.prop], scope.row) }}
              </template>

              <!-- 标签显示 -->
              <template v-else-if="column.tag && scope.row[column.prop]">
                <el-tag
                  :type="getTagType(scope.row[column.prop], column)"
                  :size="column.tagSize || 'small'"
                  effect="plain"
                >
                  {{ getTagText(scope.row[column.prop], column) }}
                </el-tag>
              </template>

              <!-- 状态显示 -->
              <template v-else-if="column.status && scope.row[column.prop]">
                <el-tag
                  :type="getStatusType(scope.row[column.prop], column)"
                  :size="column.tagSize || 'small'"
                >
                  {{ getStatusText(scope.row[column.prop], column) }}
                </el-tag>
              </template>

              <!-- 进度条显示 -->
              <template v-else-if="column.progress && isNumber(scope.row[column.prop])">
                <div class="progress-cell">
                  <el-progress
                    :percentage="Number(scope.row[column.prop])"
                    :show-text="false"
                    :stroke-width="6"
                  />
                  <span class="progress-text">
                    {{ scope.row[column.prop] }}%
                  </span>
                </div>
              </template>

              <!-- 默认文本显示 -->
              <template v-else>
                {{ scope.row[column.prop] }}
              </template>
            </slot>
          </template>
        </el-table-column>
      </template>

      <!-- 操作列 -->
      <el-table-column
        v-if="showActions"
        label="操作"
        :width="actionsWidth"
        :fixed="actionsFixed"
        align="center"
      >
        <template #default="scope">
          <slot name="actions" :row="scope.row" :$index="scope.$index">
            <el-button
              v-if="showView"
              link
              type="primary"
              size="small"
              @click.stop="handleView(scope.row)"
            >
              查看
            </el-button>

            <el-button
              v-if="showEdit"
              link
              type="primary"
              size="small"
              @click.stop="handleEdit(scope.row)"
            >
              编辑
            </el-button>

            <el-button
              v-if="showDelete"
              link
              type="danger"
              size="small"
              @click.stop="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </slot>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="table-pagination" v-if="showPagination && data.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 列设置对话框 -->
    <el-dialog
      v-model="showColumnDialog"
      title="列设置"
      width="500px"
    >
      <div class="column-settings">
        <el-checkbox-group v-model="visibleColumnProps">
          <el-checkbox
            v-for="column in allColumns"
            :key="column.prop"
            :label="column.prop"
          >
            {{ column.label }}
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <template #footer>
        <el-button @click="showColumnDialog = false">取消</el-button>
        <el-button type="primary" @click="applyColumnSettings">应用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Refresh, Search, Setting } from '@element-plus/icons-vue'

const props = defineProps({
  // 数据相关
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },

  // 表格配置
  border: {
    type: Boolean,
    default: true
  },
  stripe: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'default'
  },
  height: {
    type: [String, Number],
    default: null
  },
  maxHeight: {
    type: [String, Number],
    default: null
  },
  highlightCurrentRow: {
    type: Boolean,
    default: false
  },

  // 功能开关
  showToolbar: {
    type: Boolean,
    default: true
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  showExport: {
    type: Boolean,
    default: true
  },
  showSelection: {
    type: Boolean,
    default: false
  },
  showIndex: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showColumnSelector: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },

  // 操作按钮
  showView: {
    type: Boolean,
    default: true
  },
  showEdit: {
    type: Boolean,
    default: true
  },
  showDelete: {
    type: Boolean,
    default: true
  },

  // 分页配置
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  defaultPageSize: {
    type: Number,
    default: 10
  },

  // 样式配置
  actionsWidth: {
    type: [String, Number],
    default: '200'
  },
  actionsFixed: {
    type: [String, Boolean],
    default: false
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  },

  // 自定义函数
  rowClassName: {
    type: Function,
    default: null
  },
  cellClassName: {
    type: Function,
    default: null
  },
  indexMethod: {
    type: Function,
    default: null
  }
})

const emit = defineEmits([
  'refresh',
  'export',
  'selection-change',
  'row-click',
  'sort-change',
  'view',
  'edit',
  'delete',
  'size-change',
  'current-change'
])

// 响应式数据
const tableRef = ref()
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(props.defaultPageSize)
const showColumnDialog = ref(false)
const selectedRows = ref([])
const visibleColumnProps = ref([])

// 计算属性
const allColumns = computed(() => props.columns)

const visibleColumns = computed(() => {
  return allColumns.value.filter(column =>
    visibleColumnProps.value.includes(column.prop)
  )
})

const total = computed(() => props.data.length)

const filteredData = computed(() => {
  let result = [...props.data]

  // 搜索过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(search)
      )
    )
  }

  // 分页
  if (props.showPagination) {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    result = result.slice(start, end)
  }

  return result
})

// 方法
const handleRefresh = () => {
  emit('refresh')
}

const handleExport = () => {
  emit('export', props.data)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  emit('selection-change', selection)
}

const handleRowClick = (row, column, event) => {
  emit('row-click', row, column, event)
}

const handleSortChange = (sort) => {
  emit('sort-change', sort)
}

const handleView = (row) => {
  emit('view', row)
}

const handleEdit = (row) => {
  emit('edit', row)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除这条数据吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('delete', row)
  }).catch(() => {
    // 用户取消
  })
}

const handleSizeChange = (size) => {
  pageSize.value = size
  emit('size-change', size)
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  emit('current-change', page)
}

const getTagType = (value, column) => {
  if (column.tagType) {
    return typeof column.tagType === 'function'
      ? column.tagType(value)
      : column.tagType
  }

  // 默认类型映射
  const typeMap = {
    'success': 'success',
    'warning': 'warning',
    'error': 'danger',
    'info': 'info'
  }

  return typeMap[value] || 'info'
}

const getTagText = (value, column) => {
  if (column.tagMap) {
    return column.tagMap[value] || value
  }
  return value
}

const getStatusType = (value, column) => {
  if (column.statusType) {
    return typeof column.statusType === 'function'
      ? column.statusType(value)
      : column.statusType
  }

  // 默认状态类型映射
  const typeMap = {
    'active': 'success',
    'inactive': 'info',
    'pending': 'warning',
    'failed': 'danger',
    'completed': 'success',
    'running': 'primary'
  }

  return typeMap[value] || 'info'
}

const getStatusText = (value, column) => {
  if (column.statusMap) {
    return column.statusMap[value] || value
  }

  // 默认状态文本映射
  const textMap = {
    'active': '活跃',
    'inactive': '未激活',
    'pending': '待处理',
    'failed': '失败',
    'completed': '已完成',
    'running': '进行中'
  }

  return textMap[value] || value
}

const isNumber = (value) => {
  return typeof value === 'number' || !isNaN(Number(value))
}

const applyColumnSettings = () => {
  showColumnDialog.value = false
  // 设置会通过计算属性自动更新
}

const clearSelection = () => {
  if (tableRef.value) {
    tableRef.value.clearSelection()
  }
}

const toggleRowSelection = (row, selected) => {
  if (tableRef.value) {
    tableRef.value.toggleRowSelection(row, selected)
  }
}

// 初始化可见列
const initializeVisibleColumns = () => {
  visibleColumnProps.value = props.columns
    .filter(column => column.visible !== false)
    .map(column => column.prop)
}

// 监听数据变化重置分页
watch(() => props.data, () => {
  currentPage.value = 1
})

// 生命周期
onMounted(() => {
  initializeVisibleColumns()
})

// 暴露方法给父组件
defineExpose({
  clearSelection,
  toggleRowSelection,
  getSelectedRows: () => selectedRows.value
})
</script>

<style scoped>
.data-table-container {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #ebeef5;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

.column-settings {
  max-height: 400px;
  overflow-y: auto;
}

.column-settings .el-checkbox {
  display: block;
  margin-bottom: 12px;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-cell .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: #909399;
  min-width: 40px;
  text-align: right;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table .el-table__header-wrapper) {
  border-radius: 8px 8px 0 0;
}

:deep(.el-table .el-table__body-wrapper) {
  border-radius: 0 0 8px 8px;
}
</style>
