<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/pages/Datasets.vue-->
<template>
  <div class="datasets-page">
    <!-- 页面头部保持不变 -->
    <div class="page-header">
      <h2>数据集管理</h2>
      <el-button @click="loadDatasets" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-card>
      <!-- 表格部分保持不变 -->
      <template #header>
        <span>数据集列表 (共 {{ totalCount }} 个)</span>
      </template>

      <div class="table-toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索数据集名称"
          clearable
          style="width: 300px; margin-right: 16px;"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>

        <el-select v-model="filterDataType" placeholder="数据类型" clearable @change="handleSearch">
          <el-option label="CSV" value="csv" />
          <el-option label="JSON" value="json" />
          <el-option label="Excel" value="excel" />
        </el-select>
      </div>

      <el-table
        :data="datasets"
        v-loading="loading"
        :default-sort="{ prop: 'created_at', order: 'descending' }"
      >
        <!-- 表格列保持不变 -->
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column prop="name" label="数据集名称" sortable />
        <el-table-column prop="data_source_name" label="数据源" />
        <el-table-column prop="data_type" label="数据类型" sortable>
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.data_type)">
              {{ getDataTypeText(row.data_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="record_count" label="记录数" width="100" sortable>
          <template #default="{ row }">
            <el-tag :type="row.record_count > 0 ? 'success' : 'info'">
              {{ formatNumber(row.record_count || 0) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="previewDataset(row)" :disabled="row.record_count === 0">
              预览
            </el-button>
            <el-button size="small" @click="viewRecords(row)" :disabled="row.record_count === 0">
              查看数据
            </el-button>
            <el-button size="small" @click="addSampleData(row)" type="warning">
              添加示例
            </el-button>
            <el-button size="small" type="danger" @click="deleteDataset(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建数据集对话框 - 保持不变 -->

    <!-- 数据集预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="`数据集预览 - ${currentDataset?.name}`"
      width="80%"
      top="5vh"
    >
      <div v-if="previewData.length === 0" class="empty-preview">
        <el-empty description="暂无数据">
          <el-button type="primary" @click="addSampleData(currentDataset)">
            添加示例数据
          </el-button>
        </el-empty>
      </div>
      <div v-else>
        <div class="preview-info">
          <el-tag type="info">总记录数: {{ formatNumber(currentDataset?.record_count || 0) }}</el-tag>
          <el-tag>数据列: {{ previewColumns.length }} 个</el-tag>
          <el-tag type="success">预览行数: {{ previewData.length }} 行</el-tag>
        </div>

        <el-table
          :data="previewData"
          v-loading="previewLoading"
          border
          stripe
          max-height="500"
        >
          <el-table-column type="index" label="序号" width="60" fixed />
          <el-table-column
            v-for="column in previewColumns"
            :key="column"
            :prop="column"
            :label="column"
            min-width="150"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="cell-content">{{ row[column] }}</span>
            </template>
          </el-table-column>
        </el-table>

        <div class="preview-actions">
          <el-button type="primary" @click="viewRecords(currentDataset)">
            查看完整数据
          </el-button>
          <el-button @click="exportPreviewData" :loading="exporting">
            导出预览数据
          </el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 数据记录对话框（优化版） -->
    <el-dialog
      v-model="showRecordsDialog"
      :title="`数据集数据 - ${currentDataset?.name}`"
      width="95%"
      top="2vh"
      class="records-dialog"
    >
      <div class="records-container">
        <!-- 数据统计和操作栏 -->
        <div class="records-header">
          <div class="stats">
            <el-tag type="primary">总记录数: {{ formatNumber(recordsTotal) }}</el-tag>
            <el-tag type="success">当前页: {{ records.length }} 条</el-tag>
            <el-tag type="info">数据列: {{ recordKeys.length }} 个</el-tag>
          </div>
          <div class="actions">
            <el-input
              v-model="recordsSearchKeyword"
              placeholder="搜索记录..."
              clearable
              style="width: 200px; margin-right: 12px;"
              @clear="handleRecordsSearch"
              @keyup.enter="handleRecordsSearch"
            >
              <template #append>
                <el-button @click="handleRecordsSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-button type="primary" @click="addSampleData(currentDataset)" size="small">
              添加示例数据
            </el-button>
            <el-button @click="exportCurrentPage" :loading="exporting" size="small">
              导出本页
            </el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="records-table-container">
          <el-table
            :data="records"
            v-loading="recordsLoading"
            border
            stripe
            max-height="600"
            empty-text="暂无数据记录"
          >
            <el-table-column type="index" label="序号" width="60" fixed="left" />
            <el-table-column
              v-for="key in recordKeys"
              :key="key"
              :label="key"
              min-width="150"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <span class="cell-content">{{ formatCellValue(row.data[key]) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" fixed="right">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="danger" @click="deleteRecord(row)" plain>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页 -->
        <div class="records-pagination">
          <el-pagination
            v-model:current-page="recordsCurrentPage"
            v-model:page-size="recordsPageSize"
            :total="recordsTotal"
            :page-sizes="[10, 20, 50, 100, 200]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleRecordsSizeChange"
            @current-change="handleRecordsPageChange"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="showRecordsDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { datasetsAPI } from '../api/datasets'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 状态变量
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const showPreviewDialog = ref(false) // 新增预览对话框
const showRecordsDialog = ref(false)
const recordsLoading = ref(false)
const previewLoading = ref(false)
const exporting = ref(false)

// 数据变量
const datasets = ref([])
const dataSources = ref([])
const records = ref([])
const previewData = ref([]) // 预览数据
const previewColumns = ref([]) // 预览列
const currentDataset = ref(null)

// 分页和搜索
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const searchKeyword = ref('')
const filterDataType = ref('')

// 记录分页和搜索
const recordsCurrentPage = ref(1)
const recordsPageSize = ref(50) // 默认每页50条
const recordsTotal = ref(0)
const recordsSearchKeyword = ref('')

const createFormRef = ref()

// 表单数据保持不变
const createForm = reactive({
  name: '',
  data_source: '',
  data_type: '',
  description: '',
  data_structure: { fields: ['name', 'value', 'category'] }
})

// 计算属性
const recordKeys = computed(() => {
  if (records.value.length === 0) return []
  const firstRecord = records.value[0]
  if (firstRecord && firstRecord.data) {
    return Object.keys(firstRecord.data)
  }
  return []
})

// 工具函数
const getDataTypeTag = (type) => {
  const typeMap = {
    csv: 'success',
    json: 'warning',
    excel: 'primary'
  }
  return typeMap[type] || 'info'
}

const getDataTypeText = (type) => {
  const typeMap = {
    csv: 'CSV',
    json: 'JSON',
    excel: 'Excel'
  }
  return typeMap[type] || type
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatCellValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

// 数据集加载函数保持不变
const loadDatasets = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (filterDataType.value) {
      params.data_type = filterDataType.value
    }

    const response = await datasetsAPI.getDatasets(params)

    // 添加调试信息
    console.log('API响应数据:', response)
    if (response.results && response.results.length > 0) {
      console.log('第一个数据集的数据类型:', response.results[0].data_type)
      console.log('第一个数据集的所有字段:', Object.keys(response.results[0]))
    }

    datasets.value = response.results || response
    totalCount.value = response.total || response.length || 0
  } catch (error) {
    console.error('加载数据集失败:', error)
    ElMessage.error('加载数据集失败')
  } finally {
    loading.value = false
  }
}

// 新增：数据集预览功能
const previewDataset = async (dataset) => {
  currentDataset.value = dataset
  previewLoading.value = true
  showPreviewDialog.value = true

  try {
    // 只获取前100条数据作为预览
    const previewResponse = await datasetsAPI.getDatasetPreview(dataset.id, {
      limit: 100
    })

    previewData.value = previewResponse.data || previewResponse.results || []
    previewColumns.value = previewResponse.columns || []

    if (previewData.value.length === 0) {
      ElMessage.info('该数据集暂无数据')
    }
  } catch (error) {
    console.error('预览数据集失败:', error)
    ElMessage.error('预览数据失败: ' + error.message)
    previewData.value = []
    previewColumns.value = []
  } finally {
    previewLoading.value = false
  }
}

// 优化：查看完整数据记录（带分页）
const viewRecords = async (dataset) => {
  currentDataset.value = dataset
  recordsCurrentPage.value = 1
  recordsSearchKeyword.value = ''
  showRecordsDialog.value = true
  await loadRecords()
}

const loadRecords = async () => {
  if (!currentDataset.value) return

  recordsLoading.value = true
  try {
    const params = {
      dataset: currentDataset.value.id,
      page: recordsCurrentPage.value,
      page_size: recordsPageSize.value
    }

    // 添加搜索条件
    if (recordsSearchKeyword.value) {
      params.search = recordsSearchKeyword.value
    }

    const response = await datasetsAPI.getDataRecords(params)
    records.value = response.results || response
    recordsTotal.value = response.total || response.length || 0

    console.log(`加载记录: 第${recordsCurrentPage.value}页, 共${recordsTotal.value}条`)
  } catch (error) {
    console.error('加载数据记录失败:', error)
    ElMessage.error('加载数据记录失败: ' + error.message)
    records.value = []
    recordsTotal.value = 0
  } finally {
    recordsLoading.value = false
  }
}

// 记录搜索
const handleRecordsSearch = () => {
  recordsCurrentPage.value = 1
  loadRecords()
}

// 记录分页处理
const handleRecordsSizeChange = (newSize) => {
  recordsPageSize.value = newSize
  recordsCurrentPage.value = 1
  loadRecords()
}

const handleRecordsPageChange = (newPage) => {
  recordsCurrentPage.value = newPage
  loadRecords()
}

// 导出功能
const exportPreviewData = async () => {
  exporting.value = true
  try {
    const response = await datasetsAPI.exportDatasetData(currentDataset.value.id, {
      limit: 100,
      format: 'csv'
    })
    ElMessage.success('导出预览数据成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}

const exportCurrentPage = async () => {
  exporting.value = true
  try {
    const response = await datasetsAPI.exportDatasetData(currentDataset.value.id, {
      page: recordsCurrentPage.value,
      page_size: recordsPageSize.value,
      format: 'csv'
    })
    ElMessage.success('导出本页数据成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}

// 其他函数保持不变
const handleSearch = () => {
  currentPage.value = 1
  loadDatasets()
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadDatasets()
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
  loadDatasets()
}

const loadDataSources = async () => {
  try {
    dataSources.value = await datasetsAPI.getDataSources()
  } catch (error) {
    ElMessage.error('加载数据源失败')
  }
}

const handleCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      creating.value = true
      try {
        // 确保创建表单包含 data_type
        console.log('创建数据集的数据:', createForm)

        await datasetsAPI.createDataset(createForm)
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadDatasets()
      } catch (error) {
        console.error('创建数据集失败:', error)
        ElMessage.error('创建失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        creating.value = false
      }
    }
  })
}

const handleCreateClose = () => {
  createFormRef.value?.resetFields()
  Object.assign(createForm, {
    name: '',
    data_source: '',
    data_type: '',
    description: '',
    data_structure: { fields: ['name', 'value', 'category'] }
  })
}

const addSampleData = async (dataset) => {
  try {
    await ElMessageBox.confirm(
      `确定要为数据集 "${dataset.name}" 添加示例数据吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const sampleData = [
      { name: '苹果', value: 100, category: '水果' },
      { name: '香蕉', value: 80, category: '水果' },
      { name: '胡萝卜', value: 50, category: '蔬菜' },
      { name: '土豆', value: 30, category: '蔬菜' },
      { name: '牛肉', value: 200, category: '肉类' }
    ]

    // 使用批量创建
    await datasetsAPI.bulkCreateDataRecords({
      dataset: dataset.id,
      records: sampleData
    })

    ElMessage.success('示例数据添加成功')

    // 刷新显示
    if (showRecordsDialog.value) {
      await loadRecords()
    }
    if (showPreviewDialog.value) {
      await previewDataset(dataset)
    }
    await loadDatasets()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('添加示例数据失败:', error)
      ElMessage.error('添加示例数据失败: ' + error.message)
    }
  }
}

const deleteRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await datasetsAPI.deleteDataRecord(record.id)
    ElMessage.success('删除成功')

    if (currentDataset.value) {
      await loadRecords()
    }

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const deleteDataset = async (dataset) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据集 "${dataset.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await datasetsAPI.deleteDataset(dataset.id)
    ElMessage.success('删除成功')
    loadDatasets()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadDatasets()
  loadDataSources()
})
</script>

<style scoped>
.datasets-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 预览对话框样式 */
.preview-info {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preview-actions {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.empty-preview {
  text-align: center;
  padding: 40px 0;
}

/* 记录对话框样式 */
.records-dialog {
  max-width: 95vw;
}

.records-container {
  display: flex;
  flex-direction: column;
  height: 70vh;
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.records-table-container {
  flex: 1;
  overflow: hidden;
}

.records-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.cell-content {
  word-break: break-word;
}
</style>
