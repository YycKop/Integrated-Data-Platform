<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
 <!--Integrated-Data-Platform-frontend/src/components/charts/ChartPreview.vue-->
<template>
  <div class="chart-preview">
    <div class="preview-header">
      <h4>{{ chartType.name }}</h4>
      <span class="preview-badge">{{ chartType.chart_library }}</span>
    </div>
    <div class="preview-content">
      <!-- 根据图表类型显示不同的预览 -->
      <div v-if="chartType.name === '柱状图'" class="bar-preview">
        <div class="preview-chart">
          <div class="bar" v-for="i in 5" :key="i" :style="{ height: `${20 + i * 10}px` }"></div>
        </div>
      </div>

      <div v-else-if="chartType.name === '折线图'" class="line-preview">
        <div class="preview-chart">
          <svg width="100" height="60" viewBox="0 0 100 60">
            <!-- 第一条折线 -->
            <path d="M0,50 L20,40 L40,30 L60,20 L80,10 L100,15"
                  fill="none" stroke="#5470c6" stroke-width="2" />
            <!-- 第二条折线 -->
            <path d="M0,45 L20,35 L40,25 L60,30 L80,25 L100,30"
                  fill="none" stroke="#91cc75" stroke-width="2" />
          </svg>
        </div>
      </div>

      <div v-else-if="chartType.name === '饼图'" class="pie-preview">
        <div class="preview-chart">
          <div class="pie"></div>
        </div>
      </div>

      <div v-else-if="chartType.name === '散点图'" class="scatter-preview">
        <div class="preview-chart">
          <div class="scatter-dots">
            <div v-for="i in 15" :key="i" class="dot"
                 :style="{
                   left: `${Math.random() * 80 + 10}%`,
                   top: `${Math.random() * 80 + 10}%`
                 }"></div>
          </div>
        </div>
      </div>

      <div v-else-if="chartType.name === '雷达图'" class="radar-preview">
        <div class="preview-chart">
          <div class="radar"></div>
        </div>
      </div>

      <div v-else-if="chartType.name === '地图'" class="map-preview">
        <div class="preview-chart">
          <div class="map-container">
            <div class="map-region" v-for="i in 6" :key="i"
                 :class="`region-${i}`"></div>
          </div>
        </div>
      </div>

      <div v-else class="default-preview">
        <div class="preview-chart">
          <i class="el-icon-data-analysis"></i>
        </div>
      </div>
    </div>
    <div class="preview-footer">
      <small>{{ chartType.description || '暂无描述' }}</small>
    </div>
  </div>
</template>

<script setup>
defineProps({
  chartType: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.chart-preview {
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 12px;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
}

.chart-preview:hover {
  border-color: #5470c6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.chart-preview.selected {
  border-color: #5470c6;
  background-color: rgba(84, 112, 198, 0.05);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.preview-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.preview-badge {
  background: #f0f2f5;
  color: #666;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
}

.preview-content {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.preview-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 柱状图预览样式 */
.bar-preview .preview-chart {
  justify-content: space-around;
  align-items: flex-end;
  padding: 0 10px;
}

.bar-preview .bar {
  width: 8px;
  background: linear-gradient(to top, #5470c6, #91cc75);
  border-radius: 2px 2px 0 0;
  min-height: 5px;
}

/* 折线图预览样式 */
.line-preview {
  width: 100%;
  height: 100%;
}

.line-preview .preview-chart {
  width: 100%;
  height: 100%;
  padding: 5px;
}

.line-preview svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* 饼图预览样式 */
.pie-preview .pie {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: conic-gradient(
    #5470c6 0% 30%,
    #91cc75 30% 60%,
    #fac858 60% 100%
  );
}

/* 散点图预览样式 */
.scatter-preview .scatter-dots {
  position: relative;
  width: 100%;
  height: 100%;
}

.scatter-preview .dot {
  position: absolute;
  width: 6px;
  height: 6px;
  background: #5470c6;
  border-radius: 50%;
  opacity: 0.7;
}

/* 雷达图预览样式 */
.radar-preview .radar {
  width: 40px;
  height: 40px;
  background:
    radial-gradient(circle at center, transparent 30%, #5470c6 30%, #5470c6 35%, transparent 35%),
    linear-gradient(0deg, transparent 49%, #5470c6 49%, #5470c6 51%, transparent 51%),
    linear-gradient(60deg, transparent 49%, #5470c6 49%, #5470c6 51%, transparent 51%),
    linear-gradient(120deg, transparent 49%, #5470c6 49%, #5470c6 51%, transparent 51%);
  border-radius: 50%;
}

/* 地图预览样式 */
.map-preview .map-container {
  position: relative;
  width: 80px;
  height: 60px;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border-radius: 4px;
  overflow: hidden;
}

.map-preview .map-region {
  position: absolute;
  background: rgba(84, 112, 198, 0.3);
  border: 1px solid rgba(84, 112, 198, 0.5);
  border-radius: 2px;
}

.map-preview .region-1 {
  width: 30px;
  height: 20px;
  top: 10px;
  left: 10px;
}

.map-preview .region-2 {
  width: 25px;
  height: 15px;
  top: 35px;
  left: 15px;
}

.map-preview .region-3 {
  width: 20px;
  height: 18px;
  top: 15px;
  right: 15px;
}

.map-preview .region-4 {
  width: 15px;
  height: 12px;
  top: 40px;
  right: 25px;
}

.map-preview .region-5 {
  width: 18px;
  height: 14px;
  bottom: 10px;
  left: 45px;
}

.map-preview .region-6 {
  width: 22px;
  height: 16px;
  top: 25px;
  left: 40px;
}

.default-preview .preview-chart {
  color: #5470c6;
  font-size: 32px;
}

.preview-footer small {
  color: #666;
  font-size: 11px;
}
</style>
