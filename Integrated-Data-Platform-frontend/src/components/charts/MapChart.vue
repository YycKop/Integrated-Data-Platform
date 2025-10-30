<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/components/charts/MapChart.vue-->
<template>
  <div class="map-chart-container">
    <div ref="chartRef" class="map-chart" :style="{ width: '100%', height: '100%' }"></div>

    <!-- 加载状态 -->
    <div v-if="loading" class="map-loading">
      <el-icon class="is-loading">
        <Loading/>
      </el-icon>
      <span>地图数据加载中...</span>
    </div>

    <!-- 错误状态 -->
    <div v-if="error" class="map-error">
      <el-alert
        :title="error"
        type="error"
        :closable="false"
        show-icon>
      </el-alert>
    </div>

    <!-- 空数据状态 -->
    <div v-if="!loading && !error && (!mapData || mapData.length === 0)" class="map-empty">
      <el-empty description="暂无地图数据">
        <p>请检查数据配置或联系管理员</p>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted, watch, nextTick} from 'vue'
import * as echarts from 'echarts'
import {chinaGeoJSON} from '../../utils/chinaMapData.js'

echarts.registerMap('china', chinaGeoJSON)

// 定义props
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

// 响应式数据
const chartRef = ref(null)
const chartInstance = ref(null)
const loading = ref(false)
const error = ref('')
const mapData = ref([])

// 地图配置选项
const getChartOption = () => {
  const { data, config } = props

  // 处理地图数据
  const processedData = processMapData(data)

  // 更新响应式数据
  mapData.value = processedData.seriesData

  const option = {
    title: {
      text: config.title || '地图可视化',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (params.componentType === 'series') {
          return `${params.name}<br/>${params.seriesName}: ${params.value || 0}`
        }
        return params.name
      }
    },
    visualMap: {
      type: 'continuous',
      min: processedData.minValue || 0,
      max: processedData.maxValue || 100,
      text: ['高', '低'],
      calculable: true,
      inRange: {
        color: ['#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#fee090', '#fdae61', '#f46d43', '#d73027']
      },
      textStyle: {
        color: '#333'
      }
    },
    geo: {
      map: 'china',
      roam: true,
      label: {
        show: true,
        fontSize: 10
      },
      emphasis: {
        label: {
          show: true,
          color: '#fff'
        },
        itemStyle: {
          areaColor: '#389BB7'
        }
      },
      itemStyle: {
        borderColor: 'rgba(0, 0, 0, 0.2)',
        areaColor: '#f5f5f5'
      }
    },
    series: [
      {
        name: config.valueField || '数值',
        type: 'map',
        map: 'china',
        geoIndex: 0,
        data: processedData.seriesData,
        emphasis: {
          label: {
            show: true
          }
        }
      }
    ]
  }

  // 如果没有数据，显示提示
  if (!processedData.hasData) {
    option.graphic = {
      type: 'text',
      left: 'center',
      top: 'middle',
      style: {
        text: '暂无地图数据',
        fontSize: 16,
        fill: '#999'
      }
    }
  }

  return option
}

// 处理地图数据
const processMapData = (rawData) => {
  try {
    console.log('🗺️ MapChart 接收到的原始数据:', rawData)
    console.log('🗺️ 数据类型:', typeof rawData)
    console.log('🗺️ 是否为数组:', Array.isArray(rawData))

    let seriesData = []

    // 处理各种可能的数据格式
    if (Array.isArray(rawData)) {
      console.log('✅ 数据是数组格式')
      // 如果数据直接是数组
      seriesData = rawData.map(item => {
        if (typeof item === 'object' && item !== null) {
          // 尝试从常见字段中提取名称和值
          const name = item.name || item.region || item.province || item.city || item.地区 || '未知地区'
          const value = Number(item.value) || Number(item.数值) || Number(item.count) || 0

          console.log(`📍 处理地区数据: ${name} = ${value}`)
          return { name, value }
        } else if (typeof item === 'string') {
          // 如果是字符串数组，假设是地区名称
          return { name: item, value: 1 }
        }
        return { name: '未知地区', value: 0 }
      }).filter(item => item.name !== '未知地区')
    } else if (rawData && typeof rawData === 'object') {
      console.log('✅ 数据是对象格式')

      // 如果数据是对象，尝试从常见字段中提取
      if (Array.isArray(rawData.data)) {
        console.log('✅ 从 data 字段提取数据')
        seriesData = rawData.data.map(item => ({
          name: item.name || item.region || item.province || item.city || item.地区 || '未知地区',
          value: Number(item.value) || Number(item.数值) || Number(item.count) || 0
        })).filter(item => item.name !== '未知地区')
      } else if (Array.isArray(rawData.seriesData)) {
        console.log('✅ 从 seriesData 字段提取数据')
        seriesData = rawData.seriesData
      } else if (Array.isArray(rawData.series)) {
        console.log('✅ 从 series 字段提取数据')
        // 如果是系列数据，取第一个系列
        seriesData = rawData.series[0]?.data || []
      } else if (rawData.series && Array.isArray(rawData.series.data)) {
        console.log('✅ 从 series.data 字段提取数据')
        seriesData = rawData.series.data
      } else {
        // 尝试将对象转换为数组
        console.log('🔄 尝试将对象转换为数组')
        const dataArray = []
        for (const [key, value] of Object.entries(rawData)) {
          if (key !== 'config' && key !== 'categories' && key !== 'series' && key !== 'data') {
            dataArray.push({
              name: key,
              value: typeof value === 'number' ? value : 0
            })
          }
        }
        seriesData = dataArray
      }
    } else {
      console.log('❌ 无法识别的数据格式')
    }

    console.log('✅ 处理后的地图数据:', seriesData)

    // 计算数值范围
    const values = seriesData.map(item => item.value).filter(val => !isNaN(val))
    const minValue = values.length > 0 ? Math.min(...values) : 0
    const maxValue = values.length > 0 ? Math.max(...values) : 100

    console.log(`📊 数据范围: ${minValue} - ${maxValue}`)
    console.log(`📊 有效数据条数: ${seriesData.length}`)

    return {
      seriesData,
      minValue,
      maxValue,
      hasData: seriesData.length > 0
    }
  } catch (err) {
    console.error('❌ 地图数据处理错误:', err)
    return {
      seriesData: [],
      minValue: 0,
      maxValue: 100,
      hasData: false
    }
  }
}


// 初始化图表
const initChart = () => {
  if (!chartRef.value) {
    console.error('❌ 图表容器未找到')
    return
  }

  try {
    // 销毁现有实例
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }

    // 创建新实例
    chartInstance.value = echarts.init(chartRef.value)

    // 处理地图数据
    const processedData = processMapData(props.data)
    mapData.value = processedData.seriesData

    console.log('🗺️ 初始化地图数据:', processedData)

    // 设置配置
    const option = getChartOption()
    chartInstance.value.setOption(option)

    // 添加响应式
    window.addEventListener('resize', handleResize)

    console.log('✅ 地图图表初始化成功')

    // 如果没有数据，显示提示信息
    if (!processedData.hasData) {
      console.log('⚠️ 地图没有数据，显示空状态')
    }
  } catch (err) {
    console.error('❌ 地图图表初始化失败:', err)
    error.value = `地图初始化失败: ${err.message}`
  }
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

// 更新图表数据
const updateChart = () => {
  if (!chartInstance.value) {
    initChart()
    return
  }

  try {
    const option = getChartOption()
    chartInstance.value.setOption(option, true)
    console.log('✅ 地图图表数据更新成功')
  } catch (err) {
    console.error('❌ 地图图表更新失败:', err)
    error.value = `地图更新失败: ${err.message}`
  }
}

// 监听数据变化
watch(
  () => [props.data, props.config],
  () => {
    console.log('🔄 地图数据或配置发生变化，更新图表...')
    nextTick(() => {
      updateChart()
    })
  },
  {deep: true}
)

// 生命周期
onMounted(() => {
  console.log('🗺️ 地图组件挂载，开始初始化...')
  loading.value = true

  // 延迟初始化以确保DOM已渲染
  setTimeout(() => {
    initChart()
    loading.value = false
  }, 100)
})

onUnmounted(() => {
  // 清理资源
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.map-chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: #fff;
  border-radius: 4px;
}

.map-chart {
  width: 100%;
  height: 100%;
}

.map-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #409EFF;
  z-index: 10;
}

.map-loading .el-icon {
  font-size: 24px;
  animation: rotating 2s linear infinite;
}

.map-error {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  z-index: 10;
}

.map-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
