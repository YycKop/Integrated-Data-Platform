<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/components/charts/RadarChart.vue -->
<template>
  <div class="radar-chart-container">
    <div v-if="!hasValidData" class="no-data">
      <el-empty description="暂无有效雷达图数据">
        <p class="error-details">{{ errorMessage }}</p>
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

// 数据验证
const hasValidData = computed(() => {
  if (!props.data) {
    return false
  }

  const radarData = convertToRadarFormat(props.data)
  const hasIndicators = Array.isArray(radarData.indicators) && radarData.indicators.length > 0
  const hasSeries = Array.isArray(radarData.series) && radarData.series.length > 0

  return hasIndicators && hasSeries
})

const errorMessage = computed(() => {
  if (!props.data) return '数据为空'

  const radarData = convertToRadarFormat(props.data)
  if (!radarData.indicators || radarData.indicators.length === 0) {
    return '指标数据为空'
  }
  if (!radarData.series || radarData.series.length === 0) {
    return '系列数据为空'
  }

  return '数据格式不支持或数据为空'
})

// 数据转换函数
const convertToRadarFormat = (rawData) => {
  if (!rawData) {
    return { indicators: [], series: [] }
  }

  // 处理嵌套的data字段
  let dataToProcess = rawData.data || rawData

  // 如果已经是标准雷达图格式
  if (dataToProcess.indicators && dataToProcess.series) {
    // 统一数据字段：优先使用value，其次使用data
    const validatedSeries = dataToProcess.series.map((series) => {
      let dataArray = []
      if (Array.isArray(series.value)) {
        dataArray = series.value
      } else if (Array.isArray(series.data)) {
        dataArray = series.data
      }

      return {
        name: series.name,
        value: dataArray,
        data: dataArray
      }
    })

    return {
      indicators: Array.isArray(dataToProcess.indicators) ? dataToProcess.indicators : [],
      series: Array.isArray(validatedSeries) ? validatedSeries : []
    }
  }

  // 处理后端可能返回的其他格式
  if (dataToProcess.series && Array.isArray(dataToProcess.series)) {
    const series = dataToProcess.series.map((item) => ({
      name: item.name,
      value: item.value || item.data || [],
      data: item.value || item.data || []
    }))

    // 如果没有indicators，从第一个series的数据长度创建默认indicators
    const indicators = dataToProcess.indicators || []
    if (indicators.length === 0 && series.length > 0 && series[0].value) {
      const firstSeries = series[0]
      for (let i = 0; i < firstSeries.value.length; i++) {
        indicators.push({
          name: `指标${i + 1}`,
          max: 100
        })
      }
    }

    return { indicators, series }
  }

  return { indicators: [], series: [] }
}

const initChart = async () => {
  if (!chartRef.value) return

  await nextTick()

  const container = chartRef.value
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    setTimeout(initChart, 100)
    return
  }

  try {
    if (chartInstance) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(container)
    updateChart()

    window.addEventListener('resize', handleResize)
  } catch (error) {
    console.error('雷达图初始化失败:', error)
  }
}

// 主要图表更新函数
const updateChart = () => {
  if (!chartInstance || !hasValidData.value) return

  try {
    const radarData = convertToRadarFormat(props.data)
    const indicators = radarData.indicators || []
    const seriesData = radarData.series || []

    // 计算统一的最大值
    let unifiedMaxValue = 0

    // 收集所有系列的所有数据值
    const allDataValues = []
    seriesData.forEach(series => {
      const dataArray = series.value || series.data || []
      if (Array.isArray(dataArray)) {
        dataArray.forEach(value => {
          const numValue = Number(value) || 0
          allDataValues.push(numValue)
        })
      }
    })

    if (allDataValues.length > 0) {
      const actualMax = Math.max(...allDataValues)
      // 计算统一的最大值：实际最大值的1.5倍，向上取整到最近的5的倍数
      unifiedMaxValue = Math.ceil(actualMax * 1.5 / 5) * 5
      // 确保最小值至少为10
      unifiedMaxValue = Math.max(unifiedMaxValue, 10)
    } else {
      unifiedMaxValue = 5 // 默认值
    }

    // 所有指标使用相同的最大值
    const indicatorConfig = indicators.map((indicator) => ({
      name: indicator.name,
      max: unifiedMaxValue
    }))

    // 构建系列数据
    const seriesConfig = {
      type: 'radar',
      data: seriesData.map((series, index) => {
        const dataArray = series.value || series.data || []

        // 数据验证和转换
        let validatedData = []
        if (Array.isArray(dataArray)) {
          validatedData = dataArray.map(item => {
            const num = Number(item)
            return isNaN(num) ? 0 : num
          })
        } else {
          validatedData = new Array(indicatorConfig.length).fill(0)
        }

        return {
          value: validatedData,
          name: series.name,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 2,
            color: getRadarColor(index)
          },
          areaStyle: {
            color: getRadarColor(index),
            opacity: 0.3
          },
          itemStyle: {
            color: getRadarColor(index),
            borderWidth: 2,
            borderColor: '#fff'
          }
        }
      })
    }

    // 构建ECharts配置
    const option = {
      backgroundColor: 'transparent',
      title: {
        text: props.config.title || '雷达图',
        left: 'center',
        textStyle: {
          fontSize: 16,
          color: '#333'
        }
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        data: seriesData.map(s => s.name),
        top: 40,
        textStyle: {
          color: '#666'
        }
      },
      radar: {
        indicator: indicatorConfig,
        radius: '70%',
        splitNumber: 5,
        shape: props.config.radarShape || 'polygon',
        axisName: {
          color: '#666',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        splitArea: {
          show: true,
          areaStyle: {
            color: ['rgba(255,255,255,0.5)', 'rgba(255,255,255,0.3)']
          }
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(0, 0, 0, 0.2)'
          }
        }
      },
      series: [seriesConfig]
    }

    // 清除并重新初始化图表
    if (chartInstance) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(chartRef.value)
    chartInstance.setOption(option, true)

    // 强制重绘
    setTimeout(() => {
      chartInstance.resize()
    }, 100)

  } catch (error) {
    console.error('雷达图渲染错误:', error)
  }
}

const getRadarColor = (index) => {
  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
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
.radar-chart-container {
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
}
</style>
