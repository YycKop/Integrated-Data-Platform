<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/charts/LineChart.vue-->
<template>
  <div class="line-chart-container">
    <div v-if="!hasValidData" class="no-data">
      <el-empty description="暂无有效折线图数据">
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
    series: props.data.series,
    config: props.config
  }
})

// 获取配置值，支持回退到默认值
const getConfigValue = (key, defaultValue) => {
  return props.config?.[key] !== undefined ? props.config[key] : defaultValue
}

// 获取系列样式配置
const getSeriesStyle = (series, index) => {
  const lineStyles = getConfigValue('lineStyles', [])
  const styleConfig = lineStyles[index] || {}

  return {
    color: styleConfig.color || getLineColor(index),
    width: styleConfig.width || 3,
    showSymbol: styleConfig.showSymbol !== undefined ? styleConfig.showSymbol : true,
    smooth: styleConfig.smooth !== undefined ? styleConfig.smooth : getConfigValue('smooth', true),
    areaStyle: styleConfig.areaStyle !== undefined ? styleConfig.areaStyle : getConfigValue('areaStyle', false),
    // 新增：Y轴索引配置
    yAxisIndex: styleConfig.yAxisIndex !== undefined ? styleConfig.yAxisIndex : (index === 0 ? 0 : 1)
  }
}

// 计算是否需要双Y轴
const hasMultipleYAxes = computed(() => {
  if (!props.data?.series || props.data.series.length <= 1) return false

  // 检查是否有系列配置了不同的Y轴
  const lineStyles = getConfigValue('lineStyles', [])
  const yAxisIndices = new Set()

  props.data.series.forEach((series, index) => {
    const styleConfig = lineStyles[index] || {}
    const yAxisIndex = styleConfig.yAxisIndex !== undefined ? styleConfig.yAxisIndex : (index === 0 ? 0 : 1)
    yAxisIndices.add(yAxisIndex)
  })

  return yAxisIndices.size > 1
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
    console.error('折线图初始化失败:', error)
  }
}

const updateChart = () => {
  if (!chartInstance || !hasValidData.value) return

  try {
    const useDualYAxis = hasMultipleYAxes.value
    const smooth = props.config.smooth || false
    const areaStyle = props.config.areaStyle || false
    const showLabel = props.config.lineShowLabel || false  // 使用特定字段名
    console.log('📊 使用双Y轴:', useDualYAxis)

    const option = {
      backgroundColor: 'transparent',
      title: {
        text: getConfigValue('title', '折线图'),
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
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          },
          crossStyle: {
            color: '#999'
          }
        },
        formatter: function (params) {
          let result = `<div style="font-weight: bold; margin-bottom: 8px;">${params[0].axisValue}</div>`
          params.forEach(param => {
            const value = param.value
            const formattedValue = formatValue(value)
            const seriesName = param.seriesName
            const color = param.color

            result += `
              <div style="display: flex; align-items: center; margin: 4px 0;">
                <span style="display: inline-block; width: 10px; height: 10px; background: ${color}; border-radius: 50%; margin-right: 8px;"></span>
                <span style="flex: 1;">${seriesName}:</span>
                <span style="font-weight: bold; margin-left: 8px;">${formattedValue}</span>
              </div>
            `
          })
          return result
        }
      },
      legend: {
        data: props.data.series.map(s => s.name),
        top: 50,
        textStyle: {
          color: '#6b7280'
        },
        type: 'scroll',
        pageTextStyle: {
          color: '#6b7280'
        }
      },
      grid: {
        left: '3%',
        right: useDualYAxis ? '4%' : '4%',
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
          rotate: getConfigValue('xAxisRotate', 0),
          fontSize: 12,
          interval: getConfigValue('xAxisInterval', 'auto')
        },
        axisTick: {
          alignWithLabel: true,
          lineStyle: {
            color: '#d1d5db'
          }
        },
        splitLine: {
          show: getConfigValue('xAxisSplitLine', false),
          lineStyle: {
            color: '#f3f4f6'
          }
        }
      },
      yAxis: useDualYAxis ? [
        // 左侧Y轴
        {
          type: 'value',
          position: 'left',
          name: props.data.series[0]?.name || '数值1',
          nameTextStyle: {
            color: '#6b7280',
            fontSize: 12
          },
          axisLine: {
            lineStyle: {
              color: getLineColor(0)
            }
          },
          axisLabel: {
            color: '#6b7280',
            formatter: function (value) {
              return formatValue(value)
            }
          },
          splitLine: {
            lineStyle: {
              color: '#f3f4f6',
              type: 'dashed'
            }
          },
          scale: getConfigValue('yAxisScale', false)
        },
        // 右侧Y轴
        {
          type: 'value',
          position: 'right',
          name: props.data.series[1]?.name || '数值2',
          nameTextStyle: {
            color: '#6b7280',
            fontSize: 12
          },
          axisLine: {
            lineStyle: {
              color: getLineColor(1)
            }
          },
          axisLabel: {
            color: '#6b7280',
            formatter: function (value) {
              return formatValue(value)
            }
          },
          splitLine: {
            show: false // 右侧Y轴通常不显示分割线，避免与左侧重叠
          },
          scale: getConfigValue('yAxisScale', false)
        }
      ] : [
        // 单Y轴配置
        {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#d1d5db'
            }
          },
          axisLabel: {
            color: '#6b7280',
            formatter: function (value) {
              return formatValue(value)
            }
          },
          splitLine: {
            lineStyle: {
              color: '#f3f4f6',
              type: 'dashed'
            }
          },
          scale: getConfigValue('yAxisScale', false)
        }
      ],
      dataZoom: getConfigValue('showDataZoom', false) ? [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          start: 0,
          end: 100,
          handleSize: '80%',
          handleStyle: {
            color: '#fff',
            shadowBlur: 3,
            shadowColor: 'rgba(0, 0, 0, 0.6)',
            shadowOffsetX: 2,
            shadowOffsetY: 2
          }
        }
      ] : [],
      series: props.data.series.map((series, index) => {
        const style = getSeriesStyle(series, index)

        const seriesConfig = {
          name: series.name,
          type: 'line',
          data: series.data,
          smooth: style.smooth,
          symbol: style.showSymbol ? 'circle' : 'none',
          symbolSize: style.showSymbol ? 6 : 0,
          lineStyle: {
            width: style.width,
            color: style.color,
            type: series.lineType || 'solid'
          },
          itemStyle: {
            color: style.color,
            borderColor: '#fff',
            borderWidth: style.showSymbol ? 2 : 0
          },
          emphasis: {
            focus: 'series',
            scale: true,
            itemStyle: {
              borderWidth: 3,
              borderColor: '#fff',
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          },
          label: {
            show: getConfigValue('showLabel', false),
            position: 'top',
            color: '#374151',
            fontSize: 11,
            formatter: function (params) {
              return formatValue(params.value)
            }
          }
        }

        // 设置Y轴索引
        if (useDualYAxis) {
          seriesConfig.yAxisIndex = style.yAxisIndex
        }

        // 面积图配置
        if (style.areaStyle) {
          seriesConfig.areaStyle = {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: style.color + '80' },
              { offset: 1, color: style.color + '10' }
            ])
          }
        }

        // 标记点和标记线
        if (series.markPoint) {
          seriesConfig.markPoint = { data: series.markPoint }
        }
        if (series.markLine) {
          seriesConfig.markLine = { data: series.markLine }
        }

        // 堆叠和阶梯线
        if (series.stack) {
          seriesConfig.stack = series.stack
        }
        if (series.step) {
          seriesConfig.step = series.step
        }

        return seriesConfig
      })
    }

    console.log('🎯 图表配置:', {
      使用双Y轴: useDualYAxis,
      系列数量: props.data.series.length,
      各系列Y轴索引: props.data.series.map((s, i) => getSeriesStyle(s, i).yAxisIndex)
    })

    chartInstance.setOption(option, true)

    // 添加图表事件
    chartInstance.off('click')
    chartInstance.on('click', (params) => {
      console.log('折线图点击事件:', params)
    })

    // 确保图表正确渲染
    setTimeout(() => {
      chartInstance.resize()
    }, 50)

  } catch (error) {
    console.error('折线图渲染错误:', error)
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

const getLineColor = (index) => {
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
.line-chart-container {
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
  .line-chart-container {
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
