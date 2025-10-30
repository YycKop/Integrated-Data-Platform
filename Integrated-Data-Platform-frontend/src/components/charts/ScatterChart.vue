<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!-- Integrated-Data-Platform-frontend/src/components/charts/ScatterChart.vue -->
<template>
  <div class="scatter-chart-container">
    <div v-if="!hasValidData" class="no-data">
      <el-empty description="暂无有效散点图数据">
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

// 修复数据验证逻辑
const hasValidData = computed(() => {
  if (!props.data) {
    console.log('❌ 数据为空')
    return false
  }

  // 检查多种可能的数据格式
  const dataToCheck = props.data.data || props.data

  // 检查是否是数组格式 [ [x1, y1], [x2, y2], ... ]
  if (Array.isArray(dataToCheck) && dataToCheck.length > 0) {
    const isValid = dataToCheck.every(item =>
      Array.isArray(item) &&
      item.length >= 2 &&
      !isNaN(parseFloat(item[0])) &&
      !isNaN(parseFloat(item[1]))
    )
    console.log('✅ 数组格式数据验证:', isValid, '数据长度:', dataToCheck.length)
    return isValid
  }

  // 检查是否是对象数组格式 [ {x: val, y: val}, ... ]
  if (Array.isArray(dataToCheck) && dataToCheck.length > 0 &&
      typeof dataToCheck[0] === 'object') {
    const isValid = dataToCheck.every(item =>
      item &&
      item.x !== undefined &&
      item.y !== undefined &&
      !isNaN(parseFloat(item.x)) &&
      !isNaN(parseFloat(item.y))
    )
    console.log('✅ 对象格式数据验证:', isValid, '数据长度:', dataToCheck.length)
    return isValid
  }

  console.log('❌ 数据格式不支持:', dataToCheck)
  return false
})

const errorMessage = computed(() => {
  if (!props.data) return '数据为空'

  const dataToCheck = props.data.data || props.data
  if (!Array.isArray(dataToCheck)) return '数据不是数组格式'
  if (dataToCheck.length === 0) return '数据数组为空'
  if (!dataToCheck.every(item => Array.isArray(item) && item.length >= 2)) {
    return '数据项格式错误，期望 [x, y] 数组'
  }
  return '数据格式错误'
})

const debugInfo = computed(() => {
  if (!props.data) return null
  return {
    data: props.data.data || props.data,
    dataType: typeof props.data,
    isArray: Array.isArray(props.data),
    dataLength: Array.isArray(props.data) ? props.data.length : 'N/A',
    config: props.config
  }
})

// 修复数据转换函数
const convertDataToScatterFormat = (rawData) => {
  if (!rawData) return []

  const dataToConvert = rawData.data || rawData

  if (Array.isArray(dataToConvert) && dataToConvert.length > 0) {
    // 格式1: [ [x1, y1], [x2, y2], ... ]
    if (Array.isArray(dataToConvert[0])) {
      return dataToConvert.map(item => {
        if (item.length >= 2) {
          const x = parseFloat(item[0]) || 0
          const y = parseFloat(item[1]) || 0
          const z = item.length >= 3 ? parseFloat(item[2]) || 1 : 1
          return [x, y, z]
        }
        return [0, 0, 1]
      })
    }

    // 格式2: [ {x: val, y: val}, ... ]
    if (typeof dataToConvert[0] === 'object') {
      return dataToConvert.map(item => {
        const x = parseFloat(item.x) || parseFloat(item.valueX) || 0
        const y = parseFloat(item.y) || parseFloat(item.valueY) || 0
        const z = parseFloat(item.z) || parseFloat(item.size) || 1
        return [x, y, z]
      })
    }
  }

  console.warn('⚠️ 无法识别的数据格式:', dataToConvert)
  return []
}

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
    console.error('散点图初始化失败:', error)
  }
}

const updateChart = () => {
  if (!chartInstance || !hasValidData.value) return

  try {
    const scatterData = convertDataToScatterFormat(props.data)
    const xField = props.data.xField || props.config.xField || 'X'
    const yField = props.data.yField || props.config.yField || 'Y'

    console.log('📊 转换后的散点图数据:', scatterData)

    // 计算数据范围
    const xValues = scatterData.map(point => point[0] || 0)
    const yValues = scatterData.map(point => point[1] || 0)
    const zValues = scatterData.map(point => point[2] || 1)

    const xMin = Math.min(...xValues)
    const xMax = Math.max(...xValues)
    const yMin = Math.min(...yValues)
    const yMax = Math.max(...yValues)

    const option = {
      backgroundColor: 'transparent',
      title: {
        text: props.config.title || '散点图',
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
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        textStyle: {
          color: '#374151'
        },
        formatter: function (params) {
          const point = params.value
          let result = `${params.seriesName}<br/>`
          result += `${xField}: ${point[0].toFixed(2)}<br/>`
          result += `${yField}: ${point[1].toFixed(2)}`
          if (point[2] && point[2] !== 1) {
            result += `<br/>大小: ${point[2]}`
          }
          return result
        }
      },
      legend: {
        show: false
      },
      grid: {
        left: '3%',
        right: '3%',
        bottom: '12%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: xField,
        nameLocation: 'end',
        nameTextStyle: {
          padding: [10, 0, 0, 0],
          color: '#6b7280',
          fontSize: 12,
          fontWeight: 'bold'
        },
        axisLine: {
          lineStyle: {
            color: '#d1d5db'
          }
        },
        axisLabel: {
          color: '#6b7280',
          fontSize: 11
        },
        splitLine: {
          lineStyle: {
            color: '#f3f4f6',
            type: 'dashed'
          }
        },
        min: xMin - (xMax - xMin) * 0.05,
        max: xMax + (xMax - xMin) * 0.05
      },
      yAxis: {
        type: 'value',
        name: yField,
        nameLocation: 'end',
        nameTextStyle: {
          padding: [0, 0, 10, 0],
          color: '#6b7280',
          fontSize: 12,
          fontWeight: 'bold'
        },
        axisLine: {
          lineStyle: {
            color: '#d1d5db'
          }
        },
        axisLabel: {
          color: '#6b7280',
          fontSize: 11
        },
        splitLine: {
          lineStyle: {
            color: '#f3f4f6',
            type: 'dashed'
          }
        },
        min: yMin - (yMax - yMin) * 0.05,
        max: yMax + (yMax - yMin) * 0.05
      },
      series: [
        {
          name: '数据点',
          type: 'scatter',
          data: scatterData,
          symbolSize: function (data) {
            // 根据第三维数据调整点的大小，如果没有第三维则使用默认大小
            const zValue = data[2] || 1
            const baseSize = props.config.baseSymbolSize || 8
            const maxSize = props.config.maxSymbolSize || 20
            return Math.min(baseSize + (zValue / Math.max(...zValues)) * (maxSize - baseSize), maxSize)
          },
          itemStyle: {
            color: function (params) {
              // 根据数据值设置颜色渐变
              const xValue = params.value[0]
              const yValue = params.value[1]
              const xRatio = (xValue - xMin) / (xMax - xMin)
              const yRatio = (yValue - yMin) / (yMax - yMin)

              const colors = [
                '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'
              ]
              const colorIndex = Math.floor((xRatio + yRatio) / 2 * (colors.length - 1))
              return colors[colorIndex] || colors[0]
            },
            opacity: props.config.pointOpacity || 0.7,
            borderColor: '#fff',
            borderWidth: 1
          },
          emphasis: {
            focus: 'self',
            scale: true,
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
              borderWidth: 2,
              opacity: 1
            }
          },
          label: {
            show: props.config.showLabel || false,
            formatter: function (params) {
              return `(${params.value[0].toFixed(1)}, ${params.value[1].toFixed(1)})`
            },
            position: 'top',
            color: '#374151',
            fontSize: 10,
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            padding: [2, 4],
            borderRadius: 3
          }
        }
      ]
    }

    // 如果配置了回归线，添加回归线
    if (props.config.showRegressionLine && scatterData.length > 1) {
      const regressionData = calculateRegressionLine(scatterData)
      option.series.push({
        name: '回归线',
        type: 'line',
        data: regressionData,
        lineStyle: {
          color: '#ff6b6b',
          width: 2,
          type: 'dashed'
        },
        symbol: 'none',
        smooth: true,
        tooltip: {
          show: false
        }
      })
    }

    // 如果配置了趋势线，添加趋势线
    if (props.config.showTrendLine) {
      const trendData = calculateTrendLine(scatterData)
      option.series.push({
        name: '趋势线',
        type: 'line',
        data: trendData,
        lineStyle: {
          color: '#4ecdc4',
          width: 2
        },
        symbol: 'none',
        smooth: true,
        tooltip: {
          show: false
        }
      })
    }

    chartInstance.setOption(option, true)

    // 确保图表正确渲染
    setTimeout(() => {
      chartInstance.resize()
    }, 50)

  } catch (error) {
    console.error('散点图渲染错误:', error)
  }
}

// 计算回归线数据（线性回归）
const calculateRegressionLine = (data) => {
  const n = data.length
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0

  data.forEach(point => {
    const x = point[0]
    const y = point[1]
    sumX += x
    sumY += y
    sumXY += x * y
    sumX2 += x * x
  })

  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
  const intercept = (sumY - slope * sumX) / n

  const xValues = data.map(p => p[0])
  const minX = Math.min(...xValues)
  const maxX = Math.max(...xValues)

  return [
    [minX, slope * minX + intercept],
    [maxX, slope * maxX + intercept]
  ]
}

// 计算趋势线（移动平均）
const calculateTrendLine = (data, windowSize = 3) => {
  if (data.length < windowSize) return data

  const sortedData = [...data].sort((a, b) => a[0] - b[0])
  const trendData = []

  for (let i = 0; i <= sortedData.length - windowSize; i++) {
    const window = sortedData.slice(i, i + windowSize)
    const avgX = window.reduce((sum, point) => sum + point[0], 0) / windowSize
    const avgY = window.reduce((sum, point) => sum + point[1], 0) / windowSize
    trendData.push([avgX, avgY])
  }

  return trendData
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
  console.log('🔄 散点图数据变化:', props.data)
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
.scatter-chart-container {
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
}
</style>
