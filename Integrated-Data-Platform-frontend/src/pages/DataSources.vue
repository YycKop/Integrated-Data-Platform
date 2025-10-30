<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/pages/DataSources.vue-->
<template>
  <div class="data-sources-page">
    <div class="page-header">
      <h2>数据源管理</h2>
      <div class="header-actions">
        <el-button @click="loadDataSources" :loading="loading">
          <el-icon>
            <Refresh/>
          </el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon>
            <Plus/>
          </el-icon>
          新建数据源
        </el-button>
      </div>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据源列表 (共 {{ dataSources.length }} 个)</span>
          <div class="filter-actions">
            <el-select v-model="filterType" placeholder="筛选类型" clearable
                       @change="filterDataSources">
              <el-option label="文件上传" value="file"/>
              <el-option label="数据库" value="database"/>
              <el-option label="API接口" value="api"/>
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="filteredDataSources" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80"/>
        <el-table-column prop="name" label="数据源名称" min-width="150"/>
        <el-table-column prop="type" label="数据源类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getSourceTypeTag(row.type)">
              {{ getSourceTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip min-width="200"/>
        <el-table-column label="文件信息" width="120" v-if="filterType === 'file'">
          <template #default="{ row }">
            <el-tag v-if="row.uploaded_files && row.uploaded_files.length > 0" type="success"
                    size="small">
              {{ row.uploaded_files.length }} 个文件
            </el-tag>
            <el-tag v-else type="info" size="small">
              无文件
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建者" width="120"/>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.type === 'file'" size="small" @click="uploadFile(row)"
                       type="success">
              <el-icon>
                <Upload/>
              </el-icon>
              上传文件
            </el-button>
            <el-button size="small" @click="viewDataSource(row)">查看</el-button>
            <el-button size="small" @click="editDataSource(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDataSource(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑数据源对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingDataSource ? '编辑数据源' : '新建数据源'"
      width="700px"
      @close="handleDialogClose"
    >
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
      >
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据源名称，如：销售数据文件"/>
        </el-form-item>

        <el-form-item label="数据源类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择数据源类型" @change="handleTypeChange">
            <el-option label="文件上传" value="file"/>
            <el-option label="数据库" value="database"/>
            <el-option label="API接口" value="api"/>
          </el-select>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入数据源描述"
          />
        </el-form-item>

        <!-- 动态配置表单 -->
        <div v-if="form.type" class="config-section">
          <h4>连接配置</h4>

          <!-- 文件上传配置 -->
          <div v-if="form.type === 'file'" class="config-form">
            <el-form-item label="文件类型" prop="connection_config.file_type">
              <el-select v-model="form.connection_config.file_type" placeholder="选择文件类型">
                <el-option label="CSV" value="csv"/>
                <el-option label="Excel" value="excel"/>
                <el-option label="JSON" value="json"/>
              </el-select>
            </el-form-item>

            <el-form-item label="编码格式" prop="connection_config.encoding">
              <el-select v-model="form.connection_config.encoding" placeholder="选择编码">
                <el-option label="UTF-8" value="utf-8"/>
                <el-option label="GBK" value="gbk"/>
                <el-option label="GB2312" value="gb2312"/>
              </el-select>
            </el-form-item>

            <el-form-item label="包含表头" prop="connection_config.has_header">
              <el-switch v-model="form.connection_config.has_header"/>
            </el-form-item>
          </div>

          <!-- 数据库配置 -->
          <div v-else-if="form.type === 'database'" class="config-form">
            <el-form-item label="数据库类型" prop="connection_config.db_type">
              <el-select v-model="form.connection_config.db_type" placeholder="选择数据库">
                <el-option label="MySQL" value="mysql"/>
                <el-option label="PostgreSQL" value="postgresql"/>
                <el-option label="SQLite" value="sqlite"/>
              </el-select>
            </el-form-item>

            <el-form-item label="主机地址" prop="connection_config.host">
              <el-input v-model="form.connection_config.host" placeholder="localhost"/>
            </el-form-item>

            <el-form-item label="端口" prop="connection_config.port">
              <el-input v-model="form.connection_config.port" placeholder="3306"/>
            </el-form-item>

            <el-form-item label="数据库" prop="connection_config.database">
              <el-select
                v-model="form.connection_config.database"
                placeholder="选择数据库"
                filterable
                allow-create
              >
                <el-option
                  v-for="db in availableDatabases"
                  :key="db"
                  :label="db"
                  :value="db"
                />
              </el-select>
              <el-button
                v-if="form.connection_config.host && form.connection_config.username"
                @click="loadDatabases"
                size="small"
                :loading="loadingDatabases"
              >
                刷新数据库列表
              </el-button>
            </el-form-item>

            <el-form-item label="用户名" prop="connection_config.username">
              <el-input v-model="form.connection_config.username"/>
            </el-form-item>

            <el-form-item label="密码" prop="connection_config.password">
              <el-input v-model="form.connection_config.password" type="password" show-password/>
            </el-form-item>
          </div>

          <!-- API配置 -->
          <div v-else-if="form.type === 'api'" class="config-form">
            <el-form-item label="API地址" prop="connection_config.url">
              <el-input v-model="form.connection_config.url"
                        placeholder="https://api.example.com/data"/>
            </el-form-item>

            <el-form-item label="请求方法" prop="connection_config.method">
              <el-select v-model="form.connection_config.method" placeholder="选择请求方法">
                <el-option label="GET" value="GET"/>
                <el-option label="POST" value="POST"/>
              </el-select>
            </el-form-item>

            <el-form-item label="认证类型" prop="connection_config.auth_type">
              <el-select v-model="form.connection_config.auth_type" placeholder="选择认证方式">
                <el-option label="无认证" value="none"/>
                <el-option label="API Key" value="api_key"/>
                <el-option label="Bearer Token" value="bearer"/>
              </el-select>
            </el-form-item>

            <el-form-item v-if="form.connection_config.auth_type !== 'none'" label="认证信息"
                          prop="connection_config.auth_info">
              <el-input v-model="form.connection_config.auth_info" placeholder="API Key或Token"/>
            </el-form-item>

            <el-form-item label="请求头" prop="connection_config.headers">
              <el-input
                v-model="headersJson"
                type="textarea"
                :rows="3"
                placeholder='{"Content-Type": "application/json"}'
              />
            </el-form-item>
          </div>

          <!-- 高级配置 -->
          <div class="advanced-config">
            <el-collapse>
              <el-collapse-item title="高级配置">
                <el-form-item label="自定义配置">
                  <el-input
                    v-model="connectionConfigJson"
                    type="textarea"
                    :rows="4"
                    placeholder='请输入JSON格式的自定义配置'
                  />
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>

        <div v-else class="type-prompt">
          <el-alert title="请先选择数据源类型" type="info" :closable="false"/>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ editingDataSource ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 文件上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      :title="`上传文件 - ${currentDataSource?.name}`"
      width="600px"
    >
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          multiple
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :file-list="fileList"
          accept=".csv,.xlsx,.xls,.json"
        >
          <el-icon class="el-icon--upload">
            <upload-filled/>
          </el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 CSV、Excel、JSON 文件，单个文件不超过 10MB
            </div>
          </template>
        </el-upload>

        <div v-if="fileList.length > 0" class="upload-actions">
          <el-button type="primary" @click="submitUpload" :loading="uploading">
            开始上传
          </el-button>
          <el-button @click="clearFiles">清空文件</el-button>
        </div>

        <!-- 上传进度 -->
        <div v-if="uploadProgress.visible" class="upload-progress">
          <el-progress
            :percentage="uploadProgress.percentage"
            :status="uploadProgress.status"
            :text-inside="true"
            :stroke-width="20"
          />
          <div class="progress-info">
            <span>正在上传: {{ uploadProgress.currentFile }}</span>
            <span>已上传: {{ uploadProgress.uploaded }}/{{ uploadProgress.total }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showUploadDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 数据源详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`数据源详情 - ${currentDataSource?.name}`"
      width="800px"
    >
      <div v-if="currentDataSource" class="data-source-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="数据源名称">{{
              currentDataSource.name
            }}
          </el-descriptions-item>
          <el-descriptions-item label="数据源类型">
            <el-tag :type="getSourceTypeTag(currentDataSource.type)">
              {{ getSourceTypeText(currentDataSource.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述">{{
              currentDataSource.description || '无'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="创建者">{{
              currentDataSource.created_by
            }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{
              formatDate(currentDataSource.created_at)
            }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="currentDataSource?.type === 'database'" class="database-section">
          <h4>数据库操作</h4>

          <!-- 连接测试 -->
          <div class="connection-test">
            <el-button
              @click="testConnection"
              :loading="testingConnection"
              :type="currentDataSource.status === 'active' ? 'success' : 'primary'"
            >
              {{ testingConnection ? '测试中...' : '测试连接' }}
            </el-button>
            <span class="connection-status" :class="currentDataSource.status">
      状态: {{ getStatusText(currentDataSource.status) }}
    </span>
            <span v-if="currentDataSource.last_connection_test" class="last-test">
      最后测试: {{ formatDate(currentDataSource.last_connection_test) }}
    </span>
          </div>

          <!-- 表列表 -->
          <div v-if="currentDataSource.status === 'active'" class="tables-section">
            <div class="section-header">
              <h5>数据库表</h5>
              <el-button @click="loadTables" :loading="loadingTables" size="small">
                刷新表列表
              </el-button>
            </div>

            <el-table :data="databaseTables" v-loading="loadingTables" height="200">
              <el-table-column prop="name" label="表名"/>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="previewTable(row.name)">预览</el-button>
                  <el-button size="small" type="primary" @click="importTable(row.name)">导入
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 表预览对话框 -->
        <el-dialog
          v-model="showTablePreview"
          :title="`表预览 - ${previewTableName}`"
          width="90%"
          top="5vh"
        >
          <div v-if="tablePreviewData">
            <el-table :data="tablePreviewData.data" border stripe max-height="400">
              <el-table-column
                v-for="column in tablePreviewData.columns"
                :key="column"
                :prop="column"
                :label="column"
                min-width="120"
              />
            </el-table>
            <div class="preview-info">
              显示前 {{ tablePreviewData.preview_rows }} 条记录，共 {{ tablePreviewData.total_rows }}
              条记录
            </div>
          </div>
          <div v-else class="preview-loading">
            <el-skeleton :rows="5" animated/>
          </div>

          <template #footer>
            <el-button @click="showTablePreview = false">关闭</el-button>
            <el-button type="primary" @click="importTable(previewTableName)">导入此表</el-button>
          </template>
        </el-dialog>

        <!-- 文件列表 -->
        <div v-if="currentDataSource.type === 'file'" class="file-list-section">
          <h4>已上传文件</h4>
          <el-table :data="currentDataSource.uploaded_files || []" empty-text="暂无文件">
            <el-table-column prop="filename" label="文件名"/>
            <el-table-column prop="size" label="文件大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="upload_time" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.upload_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" @click="previewFile(row)">预览</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 配置信息 -->
        <div class="config-section">
          <h4>连接配置</h4>
          <el-alert
            v-if="currentDataSource.type === 'file'"
            title="文件上传数据源配置"
            type="info"
            :closable="false"
          />
          <pre class="config-json">{{
              JSON.stringify(currentDataSource.connection_config, null, 2)
            }}</pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button v-if="currentDataSource?.type === 'file'" type="primary"
                   @click="uploadFile(currentDataSource)">
          上传文件
        </el-button>
      </template>
    </el-dialog>

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="`文件预览 - ${previewFileData?.filename}`"
      width="90%"
      top="5vh"
    >
      <div v-if="previewFileData" class="file-preview">
        <div v-if="previewLoading" class="preview-loading">
          <el-skeleton :rows="10" animated/>
        </div>
        <div v-else-if="previewContent" class="preview-content">
          <el-table :data="previewContent.data" border stripe max-height="500">
            <el-table-column
              v-for="column in previewContent.columns"
              :key="column"
              :prop="column"
              :label="column"
              min-width="120"
            />
          </el-table>
          <div class="preview-info">
            <p>总行数: {{ previewContent.total_rows }} | 显示前 {{ previewContent.data.length }}
              行</p>
          </div>
        </div>
        <div v-else class="preview-error">
          <el-alert title="预览失败" type="error" :description="previewError"/>
        </div>
      </div>

      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button type="primary" @click="createDatasetFromFile">创建数据集</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive, computed, onMounted} from 'vue'
import {datasetsAPI} from '../api/datasets'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Upload, UploadFilled} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const showDetailDialog = ref(false)
const showPreviewDialog = ref(false)
const uploading = ref(false)
const previewLoading = ref(false)
const editingDataSource = ref(null)
const filterType = ref('')

const dataSources = ref([])
const currentDataSource = ref(null)
const previewFileData = ref(null)
const previewContent = ref(null)
const previewError = ref('')
const fileList = ref([])
const uploadRef = ref()

// 数据库相关状态
const testingConnection = ref(false)
const loadingTables = ref(false)
const showTablePreview = ref(false)
const databaseTables = ref([])
const tablePreviewData = ref(null)
const previewTableName = ref('')


const uploadProgress = reactive({
  visible: false,
  percentage: 0,
  status: 'success',
  currentFile: '',
  uploaded: 0,
  total: 0
})

const formRef = ref()

const form = reactive({
  name: '',
  type: '',
  description: '',
  connection_config: {}
})

const rules = {
  name: [
    {required: true, message: '请输入数据源名称', trigger: 'blur'}
  ],
  type: [
    {required: true, message: '请选择数据源类型', trigger: 'change'}
  ]
}

// 计算属性
const connectionConfigJson = computed({
  get: () => JSON.stringify(form.connection_config, null, 2),
  set: (value) => {
    try {
      form.connection_config = JSON.parse(value)
    } catch (e) {
      console.warn('JSON解析失败:', e)
    }
  }
})

const headersJson = computed({
  get: () => {
    return form.connection_config.headers ? JSON.stringify(form.connection_config.headers, null, 2) : ''
  },
  set: (value) => {
    try {
      form.connection_config.headers = JSON.parse(value)
    } catch (e) {
      console.warn('Headers JSON解析失败:', e)
    }
  }
})

const filteredDataSources = computed(() => {
  if (!filterType.value) return dataSources.value
  return dataSources.value.filter(source => source.type === filterType.value)
})

// 方法
const getSourceTypeTag = (type) => {
  const typeMap = {
    file: 'success',
    database: 'warning',
    api: 'primary'
  }
  return typeMap[type] || 'info'
}

const getSourceTypeText = (type) => {
  const typeMap = {
    file: '文件上传',
    database: '数据库',
    api: 'API接口'
  }
  return typeMap[type] || type
}

const getStatusTag = (status) => {
  const statusMap = {
    active: 'success',
    inactive: 'info',
    error: 'danger'
  }
  return statusMap[status] || 'info'
}

const loadTables = async () => {
  if (!currentDataSource.value) return

  loadingTables.value = true
  try {
    const response = await datasetsAPI.getDatabaseTables(currentDataSource.value.id)
    databaseTables.value = response.tables.map(name => ({name}))
    console.log('加载的表列表:', databaseTables.value)
  } catch (error) {
    console.error('加载表列表失败:', error)
    ElMessage.error('加载表列表失败: ' + error.message)
  } finally {
    loadingTables.value = false
  }
}
const previewTable = async (tableName) => {
  if (!currentDataSource.value) return

  previewTableName.value = tableName
  showTablePreview.value = true
  tablePreviewData.value = null

  try {
    const response = await datasetsAPI.getTablePreview(currentDataSource.value.id, tableName)
    tablePreviewData.value = response
    console.log('表预览数据:', response)
  } catch (error) {
    console.error('预览表数据失败:', error)
    ElMessage.error('预览表数据失败: ' + error.message)
  }
}

const importTable = async (tableName) => {
  if (!currentDataSource.value) return

  try {
    const datasetName = `${currentDataSource.value.name} - ${tableName}`

    await ElMessageBox.confirm(
      `确定要导入表 "${tableName}" 吗？`,
      '导入确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 显示加载状态 - 使用正确的 Element Plus 方法
    const loadingInstance = ElMessage({
      message: '正在导入表数据...',
      type: 'info',
      duration: 0, // 持续显示直到手动关闭
      showClose: true
    })

    try {
      const response = await datasetsAPI.importTable(currentDataSource.value.id, {
        table_name: tableName,
        dataset_name: datasetName
      })

      // 关闭加载提示
      loadingInstance.close()

      if (response.success) {
        ElMessage.success('表导入成功')
        showTablePreview.value = false
        console.log(`数据集创建成功，ID: ${response.dataset_id}`)

        // 可选：刷新数据集列表或跳转到数据集页面
        // await loadDatasets() // 如果需要刷新数据源列表
      } else {
        ElMessage.error('导入失败: ' + response.message)
      }
    } catch (error) {
      loadingInstance.close()
      throw error
    }

  } catch (error) {
    if (error !== 'cancel') {
      console.error('导入表失败:', error)
      ElMessage.error('导入表失败: ' + error.message)
    }
  }
}

const getStatusText = (status) => {
  const statusMap = {
    active: '活跃',
    inactive: '未激活',
    error: '错误'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadDataSources = async () => {
  loading.value = true
  try {
    dataSources.value = await datasetsAPI.getDataSources()
    console.log('加载的数据源:', dataSources.value)
  } catch (error) {
    console.error('加载数据源失败:', error)
    ElMessage.error('加载数据源失败')
  } finally {
    loading.value = false
  }
}

const handleTypeChange = (type) => {
  // 根据类型初始化配置
  form.connection_config = getDefaultConfig(type)
}

const getDefaultConfig = (type) => {
  const configs = {
    file: {
      file_type: 'csv',
      encoding: 'utf-8',
      has_header: true
    },
    database: {
      db_type: 'mysql',
      host: 'localhost',
      port: '3306',
      database: '',
      username: '',
      password: ''
    },
    api: {
      url: '',
      method: 'GET',
      auth_type: 'none',
      headers: {}
    }
  }
  return configs[type] || {}
}

const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        if (editingDataSource.value) {
          await datasetsAPI.updateDataSource(editingDataSource.value.id, form)
          ElMessage.success('更新成功')
        } else {
          await datasetsAPI.createDataSource(form)
          ElMessage.success('创建成功')
        }
        showCreateDialog.value = false
        loadDataSources()
      } catch (error) {
        console.error('保存数据源失败:', error)
        ElMessage.error(editingDataSource.value ? '更新失败' : '创建失败')
      } finally {
        saving.value = false
      }
    }
  })
}

const editDataSource = (dataSource) => {
  editingDataSource.value = dataSource
  Object.assign(form, {
    name: dataSource.name,
    type: dataSource.type,
    description: dataSource.description,
    connection_config: dataSource.connection_config || getDefaultConfig(dataSource.type)
  })
  showCreateDialog.value = true
}

// 新增的文件上传相关方法
const uploadFile = (dataSource) => {
  currentDataSource.value = dataSource
  showUploadDialog.value = true  // 现在这个变量已定义
  fileList.value = []
}

const handleFileChange = (file, fileListArray) => {
  console.log('文件选择:', file)
  console.log('当前文件列表:', fileListArray)

  // 文件大小验证 (10MB)
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }

  // 重要：更新 fileList 引用，触发响应式更新
  fileList.value = [...fileListArray]

  console.log('更新后的 fileList:', fileList.value)
  return true
}

const handleFileRemove = (file, fileListArray) => {
  console.log('文件移除:', file)
  console.log('移除后的文件列表:', fileListArray)

  // 更新 fileList
  fileList.value = [...fileListArray]
}

const clearFiles = () => {
  fileList.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  uploading.value = true

  try {
    // 重置上传进度
    uploadProgress.visible = true
    uploadProgress.percentage = 0
    uploadProgress.uploaded = 0
    uploadProgress.total = fileList.value.length
    uploadProgress.status = 'success'

    for (let i = 0; i < fileList.value.length; i++) {
      const file = fileList.value[i]

      // 更新当前文件信息
      uploadProgress.currentFile = file.name
      uploadProgress.uploaded = i
      uploadProgress.percentage = Math.round((i / fileList.value.length) * 100)

      console.log('准备上传文件:', {
        name: file.name,
        size: file.size,
        type: file.raw?.type
      })

      // 创建FormData - 确保使用正确的文件对象
      const formData = new FormData()
      const fileObj = file.raw || file
      formData.append('file', fileObj)

      // 添加文件信息
      formData.append('filename', file.name)
      formData.append('original_name', file.name)

      console.log('上传到数据源:', currentDataSource.value.id)

      try {
        const response = await datasetsAPI.uploadFile(currentDataSource.value.id, formData, {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              uploadProgress.percentage = percentCompleted
            }
          }
        })

        console.log('上传响应:', response)
        ElMessage.success(`文件 ${file.name} 上传成功`)

      } catch (fileError) {
        console.error(`文件 ${file.name} 上传失败:`, fileError)
        const errorMsg = fileError.message || '上传失败'
        ElMessage.error(`文件 ${file.name} 上传失败: ${errorMsg}`)
        uploadProgress.status = 'exception'
        continue // 继续上传其他文件
      }
    }

    // 更新最终进度
    uploadProgress.uploaded = fileList.value.length
    uploadProgress.percentage = 100

    ElMessage.success(`成功上传 ${fileList.value.length} 个文件`)

    // 关闭对话框并刷新
    setTimeout(() => {
      showUploadDialog.value = false
      clearFiles()
      loadDataSources() // 刷新数据源列表

      // 如果当前正在查看数据源详情，也刷新详情
      if (currentDataSource.value) {
        loadDataSourceFiles(currentDataSource.value.id)
      }
    }, 1000)

  } catch (error) {
    console.error('上传过程出错:', error)
    ElMessage.error(`上传过程出错: ${error.message}`)
    uploadProgress.status = 'exception'
  } finally {
    uploading.value = false
    // 3秒后隐藏进度条
    setTimeout(() => {
      uploadProgress.visible = false
    }, 3000)
  }
}

const viewDataSource = async (dataSource) => {
  currentDataSource.value = dataSource
  showDetailDialog.value = true
  console.log('查看数据源:', dataSource)

  // 如果是文件类型的数据源，加载文件列表
  if (dataSource.type === 'file') {
    await loadDataSourceFiles(dataSource.id)
  }

  // 如果是数据库类型的数据源，初始化状态
  if (dataSource.type === 'database') {
    console.log('数据库数据源，状态:', dataSource.status)
    // 确保状态字段存在
    if (!dataSource.status) {
      dataSource.status = 'inactive'
    }
  }
}

// 新增：加载数据源文件列表的方法
const loadDataSourceFiles = async (dataSourceId) => {
  try {
    const response = await datasetsAPI.getDataSourceFiles(dataSourceId)
    if (currentDataSource.value) {
      currentDataSource.value.uploaded_files = response.files || []
    }
  } catch (error) {
    console.error('加载文件列表失败:', error)
    if (currentDataSource.value) {
      currentDataSource.value.uploaded_files = []
    }
  }
}

const previewFile = async (fileInfo) => {
  previewFileData.value = fileInfo
  previewLoading.value = true
  showPreviewDialog.value = true
  previewContent.value = null
  previewError.value = ''

  try {
    console.log('开始预览文件:', fileInfo)

    let response

    try {
      console.log('调用预览API: /datasets/' + fileInfo.id + '/preview/')
      response = await datasetsAPI.getFilePreview(fileInfo.id)
      console.log('预览API响应:', response)
    } catch (previewError) {
      console.log('预览API失败，错误:', previewError)
      throw previewError
    }

    // 处理数据格式 - 检查是否有嵌套的RECORDS字段
    let finalData = response.data
    let finalColumns = response.columns
    let finalTotalRows = response.total_rows
    let finalPreviewRows = response.preview_rows

    // 如果数据只有一条且包含RECORDS字段，提取嵌套数据
    if (finalData && finalData.length === 1 && finalData[0].RECORDS) {
      console.log('检测到嵌套的RECORDS字段，进行数据提取')
      const nestedData = finalData[0].RECORDS
      finalData = nestedData.slice(0, 10)  // 取前10条
      finalColumns = nestedData.length > 0 ? Object.keys(nestedData[0]) : []
      finalTotalRows = nestedData.length
      finalPreviewRows = finalData.length
    }

    // 如果列名是RECORDS，但数据是平铺的，重新提取列名
    if (finalColumns.length === 1 && finalColumns[0] === 'RECORDS' && finalData.length > 0) {
      console.log('重新提取列名')
      finalColumns = Object.keys(finalData[0])
    }

    if (finalData && finalColumns) {
      previewContent.value = {
        columns: finalColumns,
        data: finalData,
        total_rows: finalTotalRows,
        preview_rows: finalPreviewRows
      }
      console.log('最终预览数据:', previewContent.value)
      ElMessage.success('预览加载成功')
    } else {
      throw new Error('预览数据格式不正确')
    }
  } catch (error) {
    console.error('文件预览失败:', error)
    previewError.value = error.response?.data?.error || error.message || '预览失败'

    ElMessage.error(`预览失败: ${previewError.value}`)

    // 显示错误信息
    previewContent.value = {
      columns: ['错误信息'],
      data: [{'错误信息': previewError.value}],
      total_rows: 1,
      preview_rows: 1
    }
  } finally {
    previewLoading.value = false
  }
}

const createDatasetFromFile = () => {
  if (!previewFileData.value) return

  ElMessageBox.confirm(
    `确定要基于文件 "${previewFileData.value.filename}" 创建数据集吗？`,
    '创建数据集',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    // 这里应该跳转到数据集创建页面或直接创建数据集
    ElMessage.success('开始创建数据集...')
    showPreviewDialog.value = false
    // 实际实现中应该导航到数据集创建页面
  }).catch(() => {
    // 用户取消
  })
}

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'

  // 如果大小是记录数而不是字节数，特殊处理
  if (bytes < 1024) {
    return `${bytes} 条记录`
  }

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 重命名这个重复的函数（大约在第1013行）
const testConnection = async (dataSource) => {
  if (!currentDataSource.value) {
    console.warn('没有选中数据源')
    return
  }

  console.log('开始测试数据库连接:', currentDataSource.value.id)

  testingConnection.value = true
  try {
    const response = await datasetsAPI.testConnection(currentDataSource.value.id)
    console.log('测试连接响应:', response)

    if (response.success) {
      ElMessage.success('连接测试成功')
      // 更新数据源状态
      currentDataSource.value.status = response.status
      currentDataSource.value.last_connection_test = new Date().toISOString()
    } else {
      ElMessage.error('连接测试失败: ' + response.message)
      currentDataSource.value.status = 'error'
      currentDataSource.value.error_message = response.message
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('测试连接失败: ' + (error.response?.data?.error || error.message))
    currentDataSource.value.status = 'error'
    currentDataSource.value.error_message = error.message
  } finally {
    testingConnection.value = false
  }
}

const deleteDataSource = async (dataSource) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据源 "${dataSource.name}" 吗？此操作不可恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await datasetsAPI.deleteDataSource(dataSource.id)
    ElMessage.success('删除成功')
    loadDataSources()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '',
    type: '',
    description: '',
    connection_config: {}
  })
  editingDataSource.value = null
}

const filterDataSources = () => {
  // 过滤逻辑已在计算属性中处理
}

onMounted(() => {
  loadDataSources()
})
</script>

<style scoped>
.data-sources-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.config-section {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  background: #fafafa;
}

.config-section h4 {
  margin: 0 0 16px 0;
  color: #409eff;
}

.config-form {
  margin-bottom: 16px;
}

.advanced-config {
  margin-top: 16px;
}

.type-prompt {
  margin: 20px 0;
}

.test-result {
  text-align: center;
}

.test-details {
  margin-top: 16px;
  text-align: left;
}

.test-details h4 {
  margin-bottom: 8px;
  color: #606266;
}

.test-details pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

.upload-section {
  padding: 20px;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.upload-progress {
  margin-top: 20px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}

.data-source-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.file-list-section,
.config-section {
  margin-top: 20px;
}

.config-json {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
}

.file-preview {
  min-height: 400px;
}

.preview-loading,
.preview-error {
  text-align: center;
  padding: 40px 0;
}

.preview-info {
  margin-top: 16px;
  text-align: center;
  color: #666;
}

.database-section {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  background: #fafafa;
}

.connection-test {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.connection-status.active {
  color: #67c23a;
  font-weight: bold;
}

.connection-status.error {
  color: #f56c6c;
  font-weight: bold;
}

.connection-status.inactive {
  color: #909399;
}

.last-test {
  color: #909399;
  font-size: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-info {
  margin-top: 12px;
  text-align: center;
  color: #666;
  font-size: 14px;
}
</style>
