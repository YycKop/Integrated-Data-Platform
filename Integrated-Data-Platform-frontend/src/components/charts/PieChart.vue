<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/charts/PieChart.vue-->
<template>
  <div class="pie-chart-container">
    <div v-if="!hasValidData" class="no-data">
      <el-empty description="暂无有效饼图数据">
        <p class="error-details">{{ errorMessage }}</p>
        <div v-if="debugInfo" class="debug-info">
          <el-collapse>
            <el-collapse-item title="数据详情">
              <pre>{{ JSON.stringify(debugInfo, null, 2) }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-empty>
    </div>
    <div v-else ref="chartRef" class="chart-element"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  config: {
    type: Object,
    default: () => ({})
  }
})

const chartRef = ref()
let chartInstance = null

// 计算属性检查数据有效性
const hasValidData = computed(() => {
  if (!props.data) {
    console.log('❌ 饼图数据为空')
    return false
  }

  // 支持两种数据格式：
  // 1. {data: [...]} - 标准格式
  // 2. [...] - 数组格式（兼容旧格式）
  let pieData = props.data

  // 如果数据有 data 字段，使用 data 字段
  if (props.data && props.data.data && Array.isArray(props.data.data)) {
    pieData = props.data.data
    console.log('📊 使用标准饼图数据格式: {data: [...]}')
  } else if (Array.isArray(props.data)) {
    pieData = props.data
    console.log('📊 使用兼容饼图数据格式: [...]')
  } else {
    console.log('❌ 饼图数据格式不正确:', props.data)
    return false
  }

  const hasData = Array.isArray(pieData) && pieData.length > 0

  if (!hasData) {
    console.log('❌ 饼图数据数组为空:', pieData)
    return false
  }

  // 检查每个数据项是否都有 name 和 value
  const validDataItems = pieData.every(item =>
    item && item.name !== undefined && item.value !== undefined
  )

  if (!validDataItems) {
    console.log('❌ 饼图数据项格式不正确:', pieData)
    return false
  }

  console.log('✅ 饼图数据验证通过，数据项数量:', pieData.length)
  return true
})

const errorMessage = computed(() => {
  if (!props.data) return '数据为空'
  if (!props.data.data) return '缺少数据字段'
  if (!Array.isArray(props.data.data)) return '数据不是数组格式'
  if (props.data.data.length === 0) return '数据数组为空'

  const invalidItems = props.data.data.filter(item =>
    !item || item.name === undefined || item.value === undefined
  )
  if (invalidItems.length > 0) return '数据项格式不正确'

  return '数据格式错误'
})

const debugInfo = computed(() => {
  if (!props.data) return null

  let pieData = props.data
  if (props.data && props.data.data && Array.isArray(props.data.data)) {
    pieData = props.data.data
  }

  return {
    rawData: props.data,
    processedData: pieData,
    config: props.config,
    dataType: typeof props.data,
    isStandardFormat: !!(props.data && props.data.data),
    dataLength: Array.isArray(pieData) ? pieData.length : '非数组'
  }
})

const initChart = async () => {
  if (!chartRef.value) {
    console.warn('饼图容器未找到')
    return
  }

  await nextTick()

  const container = chartRef.value
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    setTimeout(initChart, 100)
    return
  }

  try {
    chartInstance = echarts.init(container)
    updateChart()

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
  } catch (error) {
    console.error('饼图初始化失败:', error)
  }
}

const updateChart = () => {
  if (!chartInstance || !hasValidData.value) return

  try {
    // 支持两种数据格式
    let pieData = props.data
    if (props.data && props.data.data && Array.isArray(props.data.data)) {
      pieData = props.data.data
    }

    console.log('🎯 渲染饼图数据:', {
      数据项数量: pieData.length,
      数据示例: pieData.slice(0, 3),
      数据格式: props.data.data ? '标准格式 {data: [...]}' : '兼容格式 [...]'
    })

    const option = {
      backgroundColor: 'transparent',
      title: {
        text: props.config?.title || '饼图',
        left: 'center',
        textStyle: {
          fontSize: 18,
          fontWeight: 'bold',
          color: '#1f2937'
        },
        top: 10
      },
      tooltip: {
        trigger: 'item',
        formatter: function (params) {
          const { name, value, percent } = params
          return `
            <div style="font-weight: bold;">${name}</div>
            <div>数值: ${formatValue(value)}</div>
            <div>占比: ${percent}%</div>
          `
        }
      },
      legend: {
        type: 'scroll',
        orient: 'vertical',
        right: 10,
        top: 'center',
        textStyle: {
          color: '#6b7280',
          fontSize: 12
        },
        formatter: function (name) {
          // 截断过长的图例名称
          return name.length > 10 ? name.substring(0, 10) + '...' : name
        }
      },
      series: [
        {
          name: props.config?.title || '饼图',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%',
            fontSize: 12,
            color: '#374151'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: true,
            length: 10,
            length2: 10
          },
          data: pieData.map((item, index) => ({
            name: String(item.name),
            value: Number(item.value),
            itemStyle: {
              color: getPieColor(index)
            }
          }))
        }
      ]
    }

    chartInstance.setOption(option, true)

    // 添加图表事件
    chartInstance.off('click')
    chartInstance.on('click', (params) => {
      console.log('饼图点击事件:', params)
    })

    // 确保图表正确渲染
    setTimeout(() => {
      chartInstance.resize()
    }, 50)

  } catch (error) {
    console.error('饼图渲染错误:', error)
  }
}

// 数值格式化函数
const formatValue = (value) => {
  if (value === null || value === undefined) return '-'

  const absValue = Math.abs(value)
  if (absValue >= 100000000) {
    return (value / 100000000).toFixed(1) + '亿'
  }
  if (absValue >= 10000) {
    return (value / 10000).toFixed(1) + '万'
  }
  if (absValue >= 1000) {
    return (value / 1000).toFixed(1) + 'k'
  }
  if (Math.floor(value) !== value) {
    return value.toFixed(2)
  }
  return value.toString()
}

const getPieColor = (index) => {
  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc',
    '#9cdc82', '#f6c171', '#749f83', '#ca8622', '#bda29a',
    '#6e7074', '#c4ccd3', '#61a0a8', '#d48265', '#91c7ae',
    '#749f83', '#ca8622', '#bda29a', '#6e7074', '#c4ccd3'
  ]
  return colors[index % colors.length]
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  setTimeout(initChart, 100)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

// 监听数据变化
watch(() => props.data, () => {
  console.log('📊 饼图数据变化:', props.data)
  if (hasValidData.value) {
    setTimeout(updateChart, 50)
  }
}, { deep: true })

watch(() => props.config, () => {
  if (hasValidData.value) {
    setTimeout(updateChart, 50)
  }
}, { deep: true })

// 监听容器大小变化
watch(chartRef, (newRef) => {
  if (newRef && hasValidData.value) {
    setTimeout(() => {
      chartInstance?.resize()
    }, 100)
  }
})
</script>

<style scoped>
.pie-chart-container {
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 400px;
}

.chart-element {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px dashed #e5e7eb;
}

.error-details {
  margin-top: 8px;
  color: #6b7280;
  font-size: 14px;
  text-align: center;
}

.debug-info {
  margin-top: 16px;
  max-width: 100%;
}

.debug-info pre {
  background: #f8fafc;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  font-size: 12px;
  color: #374151;
  overflow: auto;
  max-height: 200px;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pie-chart-container {
    min-height: 300px;
  }

  .chart-element {
    min-height: 300px;
  }

  .no-data {
    height: 300px;
  }
}
</style>
