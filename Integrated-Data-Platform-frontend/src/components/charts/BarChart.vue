<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/charts/BarChart.vue-->
<template>
  <div class="bar-chart-container">
    <div v-if="!hasValidData" class="no-data">
      <el-empty description="暂无有效图表数据">
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
  if (!props.data) return false

  const hasCategories = props.data.categories &&
                       Array.isArray(props.data.categories) &&
                       props.data.categories.length > 0

  const hasSeries = props.data.series &&
                   Array.isArray(props.data.series) &&
                   props.data.series.length > 0

  const hasSeriesData = hasSeries &&
                       props.data.series.some(series =>
                         series.data &&
                         Array.isArray(series.data) &&
                         series.data.length > 0
                       )

  return hasCategories && hasSeries && hasSeriesData
})

const errorMessage = computed(() => {
  if (!props.data) return '数据为空'
  if (!props.data.categories) return '缺少分类数据'
  if (props.data.categories.length === 0) return '分类数据为空'
  if (!props.data.series) return '缺少系列数据'
  if (props.data.series.length === 0) return '系列数据为空'
  return '数据格式错误'
})

const debugInfo = computed(() => {
  if (!props.data) return null
  return {
    categories: props.data.categories,
    series: props.data.series
  }
})

const initChart = async () => {
  if (!chartRef.value) {
    console.warn('图表容器未找到')
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
    console.error('图表初始化失败:', error)
  }
}

const updateChart = () => {
  if (!chartInstance || !hasValidData.value) return

  try {
    const option = {
      backgroundColor: 'transparent',
      title: {
        text: props.config.title || '柱状图',
        left: 'center',
        textStyle: {
          fontSize: 18,
          fontWeight: 'bold',
          color: '#1f2937'
        },
        top: 10
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        textStyle: {
          color: '#374151'
        },
        axisPointer: {
          type: 'shadow',
          shadowStyle: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      },
      legend: {
        data: props.data.series.map(s => s.name),
        top: 50,
        textStyle: {
          color: '#6b7280'
        }
      },
      grid: {
        left: '3%',
        right: '3%',
        bottom: '12%',
        top: '20%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: props.data.categories,
        axisLine: {
          lineStyle: {
            color: '#d1d5db'
          }
        },
        axisLabel: {
          color: '#6b7280',
          rotate: 45,
          interval: 0,
          fontSize: 12,
          margin: 15
        },
        axisTick: {
          alignWithLabel: true,
          lineStyle: {
            color: '#d1d5db'
          }
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          lineStyle: {
            color: '#d1d5db'
          }
        },
        axisLabel: {
          color: '#6b7280',
          formatter: function (value) {
            if (value >= 10000) {
              return (value / 10000).toFixed(1) + '万'
            }
            if (value >= 1000) {
              return (value / 1000).toFixed(1) + 'k'
            }
            return value
          }
        },
        splitLine: {
          lineStyle: {
            color: '#f3f4f6',
            type: 'dashed'
          }
        }
      },
      series: props.data.series.map((series, index) => ({
        name: series.name,
        type: 'bar',
        data: series.data,
        barWidth: '60%',
        itemStyle: {
          color: getBarColor(index),
          borderRadius: [4, 4, 0, 0],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 4,
          shadowOffsetY: 2
        },
        emphasis: {
          itemStyle: {
            shadowColor: 'rgba(0, 0, 0, 0.2)',
            shadowBlur: 8,
            shadowOffsetY: 4
          }
        },
        label: {
          show: true,
          position: 'top',
          color: '#374151',
          fontSize: 11,
          fontWeight: 'bold',
          formatter: function (params) {
            const value = params.value
            if (value >= 10000) {
              return (value / 10000).toFixed(1) + '万'
            }
            if (value >= 1000) {
              return (value / 1000).toFixed(1) + 'k'
            }
            return value
          }
        }
      }))
    }

    chartInstance.setOption(option, true)

    // 确保图表正确渲染
    setTimeout(() => {
      chartInstance.resize()
    }, 50)

  } catch (error) {
    console.error('图表渲染错误:', error)
  }
}

const getBarColor = (index) => {
  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc',
    '#9cdc82', '#f6c171', '#749f83', '#ca8622', '#bda29a'
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
  if (hasValidData.value) {
    setTimeout(updateChart, 50)
  }
}, { deep: true })

watch(() => props.config, () => {
  if (hasValidData.value) {
    setTimeout(updateChart, 50)
  }
}, { deep: true })
</script>

<style scoped>
.bar-chart-container {
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

  .error-details {
    margin-top: 8px;
    color: #6b7280;
    font-size: 14px;
  }
}

.debug-info {
  margin-top: 16px;
  max-width: 100%;

  pre {
    background: #f8fafc;
    padding: 12px;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
    font-size: 12px;
    color: #374151;
    overflow: auto;
    max-height: 200px;
  }
}
</style>
