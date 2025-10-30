// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/utils/iconMapper.js
import {
  Histogram,
  TrendCharts,
  PieChart,
  ScatterPlot,
  DataBoard,
  DataAnalysis
} from '@element-plus/icons-vue'

export const getChartIcon = (chartType) => {
  const iconMap = {
    '柱状图': Histogram,
    '折线图': TrendCharts,
    '饼图': PieChart,
    '散点图': ScatterPlot,
    '雷达图': DataBoard
  }
  return iconMap[chartType] || DataAnalysis
}

export const iconComponents = {
  Histogram,
  TrendCharts,
  PieChart,
  ScatterPlot,
  DataBoard,
  DataAnalysis
}
