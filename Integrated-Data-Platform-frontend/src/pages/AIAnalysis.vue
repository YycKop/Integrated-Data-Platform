<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/pages/AIAnalysis.vue -->
<template>
  <div class="ai-analysis-page">
    <div class="page-header">
      <h1>智能分析</h1>
      <p class="page-description">使用AI技术深度分析农产品数据，发现隐藏的洞察和趋势</p>
    </div>

    <div class="analysis-container">
      <el-row :gutter="20">
        <!-- 左侧分析面板 -->
        <el-col :span="8">
          <analysis-panel
            :datasets="datasets"
            :loading="datasetsLoading"
            @analyze="handleAnalysis"
            @refresh-datasets="loadDatasets"
          />
        </el-col>

        <!-- 右侧结果展示 -->
        <el-col :span="16">
          <div class="results-section">
            <div class="results-header">
              <h3>分析结果</h3>
              <div class="results-actions">
                <el-button
                  type="primary"
                  :disabled="!insights.length"
                  @click="exportResults"
                >
                  <el-icon><Download /></el-icon>
                  导出报告
                </el-button>
                <el-button
                  v-if="insights.length"
                  @click="clearResults"
                >
                  <el-icon><Delete /></el-icon>
                  清空结果
                </el-button>
              </div>
            </div>

            <div class="insights-list">
              <el-empty
                v-if="!insights.length"
                description="暂无分析结果，请先进行分析"
                :image-size="100"
              />

              <insight-card
                v-for="(insight, index) in insights"
                :key="insight.id || index"
                :insight="insight"
                @delete="deleteInsight(index)"
              />
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 调试信息（开发时显示） -->
    <el-card v-if="showDebug" class="debug-card">
      <template #header>
        <span>调试信息</span>
        <el-button type="text" @click="showDebug = !showDebug">隐藏</el-button>
      </template>
      <div>
        <p>数据集数量: {{ datasets.length }}</p>
        <p>加载状态: {{ datasetsLoading }}</p>
        <pre>{{ datasets }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete } from '@element-plus/icons-vue'
import { useAIStore } from '../stores/ai'
import { datasetsAPI } from '../api/datasets' // 导入数据集API作为备选
import AnalysisPanel from '../components/ai/AnalysisPanel.vue'
import InsightCard from '../components/ai/InsightCard.vue'

const aiStore = useAIStore()

// 数据集相关状态
const datasets = ref([])
const datasetsLoading = ref(false)
const showDebug = ref(true) // 开发时显示调试信息

// 修复：确保insights有默认值
const insights = computed(() => aiStore.insights || [])

// 加载数据集列表 - 增强版本
const loadDatasets = async () => {
  datasetsLoading.value = true
  try {
    console.log('开始加载数据集列表...')

    // 方法1: 尝试使用AI模块的数据集接口
    try {
      const response = await aiStore.getAIDatasets()
      console.log('AI数据集接口响应:', response)

      if (response && response.success !== false) {
        if (Array.isArray(response)) {
          datasets.value = response
        } else if (response.data && Array.isArray(response.data)) {
          datasets.value = response.data
        } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
          datasets.value = response.data.results
        } else {
          console.warn('AI接口返回格式异常，尝试方法2')
          throw new Error('AI接口返回格式异常')
        }
      } else {
        console.warn('AI接口返回失败，尝试方法2')
        throw new Error('AI接口返回失败')
      }
    } catch (aiError) {
      console.log('AI接口失败，尝试数据集API:', aiError)

      // 方法2: 使用数据集模块的API
      const datasetsResponse = await datasetsAPI.getDatasets()
      console.log('数据集API响应:', datasetsResponse)

      if (Array.isArray(datasetsResponse)) {
        datasets.value = datasetsResponse
      } else if (datasetsResponse && Array.isArray(datasetsResponse.data)) {
        datasets.value = datasetsResponse.data
      } else if (datasetsResponse && datasetsResponse.data && Array.isArray(datasetsResponse.data.results)) {
        datasets.value = datasetsResponse.data.results
      } else {
        console.warn('数据集API返回格式异常，使用空数组')
        datasets.value = []
      }
    }

    console.log('最终数据集列表:', datasets.value)
    ElMessage.success(`成功加载 ${datasets.value.length} 个数据集`)
  } catch (error) {
    console.error('加载数据集失败:', error)
    ElMessage.error('加载数据集失败: ' + (error.message || '未知错误'))
    datasets.value = []
  } finally {
    datasetsLoading.value = false
  }
}

// 在AI Store中添加获取数据集的方法
const initializeAIStore = () => {
  if (!aiStore.getAIDatasets) {
    aiStore.getAIDatasets = async () => {
      try {
        const response = await fetch('/api/ai/models/datasets/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        return await response.json()
      } catch (error) {
        console.error('AI数据集获取失败:', error)
        throw error
      }
    }
  }
}

const handleAnalysis = async (analysisData) => {
  try {
    console.log('开始分析，数据:', analysisData)

    let result
    if (analysisData.type === 'market_trends') {
      result = await aiStore.analyzeMarketTrends(analysisData.data)
    } else {
      result = await aiStore.generateInsights(analysisData.data, analysisData.type)
    }

    console.log('分析完成，结果:', result)
    ElMessage.success('分析完成')
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败: ' + (error.message || '未知错误'))
  }
}

const deleteInsight = (index) => {
  aiStore.deleteInsight(index)
  ElMessage.success('删除成功')
}

const clearResults = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有分析结果吗？此操作不可恢复。',
      '确认清空',
      { type: 'warning' }
    )
    aiStore.clearInsights()
    ElMessage.success('已清空所有分析结果')
  } catch (error) {
    // 用户取消操作
  }
}

const exportResults = () => {
  if (!insights.value.length) {
    ElMessage.warning('没有可导出的分析结果')
    return
  }

  // 模拟导出功能
  const dataStr = JSON.stringify(insights.value, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)

  const exportFileDefaultName = `AI分析报告_${new Date().toISOString().split('T')[0]}.json`

  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()

  ElMessage.success('导出成功')
}

// 确保组件挂载时加载数据集
onMounted(() => {
  console.log('AIAnalysis页面挂载，当前insights:', insights.value)
  initializeAIStore()
  loadDatasets()
})
</script>

<style scoped>
.ai-analysis-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.analysis-container {
  min-height: 600px;
}

.results-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.results-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.results-actions {
  display: flex;
  gap: 10px;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 400px;
}

.debug-card {
  margin-top: 20px;
  background: #f5f7fa;
}
</style>
