// Copyright (c) 2025 YycKop
// MIT License
// Integrated-Data-Platform-frontend/src/utils/ai.js
// AI相关工具函数

/**
 * 格式化模型类型显示
 */
export const formatModelType = (type) => {
  const typeMap = {
    'price_prediction': '价格预测',
    'yield_prediction': '产量预测',
    'disease_detection': '病害检测',
    'market_analysis': '市场分析',
    'climate_impact': '气候影响分析'
  }
  return typeMap[type] || type
}

/**
 * 获取模型类型标签样式
 */
export const getModelTypeTag = (type) => {
  const tagMap = {
    'price_prediction': { type: 'success', color: '#67C23A' },
    'yield_prediction': { type: 'warning', color: '#E6A23C' },
    'disease_detection': { type: 'danger', color: '#F56C6C' },
    'market_analysis': { type: 'info', color: '#409EFF' },
    'climate_impact': { type: 'primary', color: '#409EFF' }
  }
  return tagMap[type] || { type: 'info', color: '#909399' }
}

/**
 * 格式化准确率显示
 */
export const formatAccuracy = (accuracy) => {
  if (accuracy === null || accuracy === undefined) return '-'
  return `${(accuracy * 100).toFixed(1)}%`
}

/**
 * 生成预测数据样本
 */
export const generateSampleData = (modelType) => {
  const samples = {
    price_prediction: [
      { 产品: '苹果', 月份: 1, 地区: '北京', 产量: 1000, 需求量: 1200 },
      { 产品: '香蕉', 月份: 1, 地区: '上海', 产量: 800, 需求量: 900 }
    ],
    yield_prediction: [
      { 作物: '水稻', 种植面积: 100, 降雨量: 1200, 温度: 25, 施肥量: 50 },
      { 作物: '小麦', 种植面积: 80, 降雨量: 800, 温度: 18, 施肥量: 40 }
    ],
    disease_detection: [
      { 作物: '番茄', 叶片颜色: '黄色', 斑点大小: '小', 生长阶段: '开花期' },
      { 作物: '黄瓜', 叶片颜色: '褐色', 斑点大小: '大', 生长阶段: '结果期' }
    ]
  }
  return samples[modelType] || []
}

/**
 * 验证训练数据
 */
export const validateTrainingData = (data, features, target) => {
  const errors = []

  if (!data || data.length === 0) {
    errors.push('训练数据不能为空')
  }

  if (!features || features.length === 0) {
    errors.push('请选择特征列')
  }

  if (!target) {
    errors.push('请选择目标列')
  }

  // 检查特征列是否存在
  features.forEach(feature => {
    if (!data[0] || !(feature in data[0])) {
      errors.push(`特征列"${feature}"在数据中不存在`)
    }
  })

  // 检查目标列是否存在
  if (target && data[0] && !(target in data[0])) {
    errors.push(`目标列"${target}"在数据中不存在`)
  }

  return errors
}

/**
 * 计算模型性能指标
 */
export const calculateModelMetrics = (predictions, actuals) => {
  if (!predictions || !actuals || predictions.length !== actuals.length) {
    return null
  }

  const n = predictions.length
  const mae = predictions.reduce((sum, pred, i) =>
    sum + Math.abs(pred - actuals[i]), 0) / n

  const mse = predictions.reduce((sum, pred, i) =>
    sum + Math.pow(pred - actuals[i], 2), 0) / n

  const rmse = Math.sqrt(mse)

  return {
    mae: Number(mae.toFixed(4)),
    mse: Number(mse.toFixed(4)),
    rmse: Number(rmse.toFixed(4))
  }
}

/**
 * 解析AI分析结果
 */
export const parseAnalysisResult = (result) => {
  if (!result) return null

  // 尝试解析JSON格式的结果
  try {
    if (typeof result === 'string') {
      return JSON.parse(result)
    }
    return result
  } catch {
    // 如果不是JSON，返回原始文本
    return {
      text: result,
      insights: extractInsightsFromText(result)
    }
  }
}

/**
 * 从文本中提取关键洞察
 */
export const extractInsightsFromText = (text) => {
  const insights = []
  const sentences = text.split(/[.!?。！？]/).filter(s => s.trim())

  sentences.forEach(sentence => {
    const trimmed = sentence.trim()
    if (trimmed.length < 10) return

    // 识别关键洞察的规则
    const keyPhrases = [
      '建议', '推荐', '趋势', '增长', '下降', '上涨', '下跌',
      '机会', '风险', '重要', '关键', '注意', '预测'
    ]

    if (keyPhrases.some(phrase => trimmed.includes(phrase))) {
      insights.push(trimmed)
    }
  })

  return insights.slice(0, 5) // 返回前5个关键洞察
}
