<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/pages/Visualization.vue-->
<template>
  <div class="visualization-page">
    <div class="page-header">
      <h1>可视化图表</h1>
      <el-button type="primary" @click="showCreateDialog = true" :loading="loading">
        <i class="el-icon-plus"></i> 创建图表
      </el-button>
    </div>

    <!-- 数据统计 -->
    <div class="data-stats" v-if="!loading && visualizations.length > 0">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-statistic title="图表总数" :value="visualizations.length"/>
        </el-col>
        <el-col :span="8">
          <el-statistic title="数据集数量" :value="datasets.length"/>
        </el-col>
        <el-col :span="8">
          <el-statistic title="图表类型" :value="chartTypes.length"/>
        </el-col>
      </el-row>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated/>
    </div>

    <!-- 空状态 -->
    <div v-else-if="visualizations.length === 0" class="empty-state">
      <el-empty description="暂无可视化图表">
        <el-button type="primary" @click="showCreateDialog = true">创建第一个图表</el-button>
      </el-empty>
    </div>

    <!-- 图表列表 -->
    <div v-else class="visualization-list">
      <el-card
        v-for="viz in visualizations"
        :key="viz.id"
        class="viz-card"
        shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <h3>{{ viz.name || '未命名图表' }}</h3>
              <el-tag
                :type="getChartTypeTagType(viz.chart_type_name)"
                size="small">
                {{ viz.chart_type_name || viz.chart_type?.name || '未知类型' }}
              </el-tag>
            </div>
            <el-dropdown @command="handleDropdownCommand($event, viz)">
  <span class="el-dropdown-link">
    <el-button type="text" icon="el-icon-more"></el-button>
  </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="view" icon="el-icon-view">
                    查看
                  </el-dropdown-item>
                  <el-dropdown-item command="edit" icon="el-icon-edit">
                    编辑
                  </el-dropdown-item>
                  <el-dropdown-item
                    command="delete"
                    icon="el-icon-delete"
                    style="color: #f56c6c;">
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>

        <div class="viz-content">
          <div class="viz-info">
            <div class="info-item">
              <i class="el-icon-document"></i>
              <span><strong>数据集:</strong> {{
                  getDatasetName(viz.dataset) || viz.dataset_name || '未知数据集'
                }}</span>
            </div>
            <div class="info-item">
              <i class="el-icon-pie-chart"></i>
              <span><strong>类型:</strong> {{
                  viz.chart_type_name || viz.chart_type?.name || '未知类型'
                }}</span>
            </div>
            <div class="info-item">
              <i class="el-icon-time"></i>
              <span><strong>创建:</strong> {{ formatDate(viz.created_at) }}</span>
            </div>
            <div class="info-item" v-if="viz.description">
              <i class="el-icon-document"></i>
              <span class="description">{{ viz.description }}</span>
            </div>
          </div>
          <div class="viz-preview">
            <div
              class="mini-chart"
              :class="getChartTypeClass(viz.chart_type_name)">
              <i :class="getChartTypeIcon(viz.chart_type_name)"></i>
            </div>
          </div>
        </div>

        <div class="card-actions">
          <el-button
            type="primary"
            size="small"
            @click="viewVisualization(viz.id)"
            icon="el-icon-view">
            查看图表
          </el-button>
          <el-button
            size="small"
            @click="editVisualization(viz)"
            icon="el-icon-edit">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteVisualization(viz.id)"
            icon="el-icon-delete"
            style="margin-left: auto;">
            删除
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="isEditing ? '编辑图表' : '创建图表'"
      v-model="showCreateDialog"
      width="800px"
      @close="resetForm">

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="图表名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入图表名称"/>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入图表描述"/>
        </el-form-item>

        <el-form-item label="数据集" prop="dataset">
          <el-select
            v-model="form.dataset"
            placeholder="请选择数据集"
            @change="onDatasetChange"
            clearable
            style="width: 100%">
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id">
              <span>{{ dataset.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                ID: {{ dataset.id }}
              </span>
            </el-option>
          </el-select>
          <div v-if="datasets.length === 0"
               style="color: #e6a23c; font-size: 12px; margin-top: 5px;">
            <i class="el-icon-warning"></i> 没有可用数据集，请先创建数据集
          </div>
        </el-form-item>

        <el-form-item label="图表类型" prop="chart_type">
          <div class="chart-type-selector">
            <div
              v-for="chartType in chartTypes"
              :key="chartType.id"
              :class="['chart-type-card', { selected: form.chart_type === chartType.id }]"
              @click="selectChartType(chartType)">
              <ChartPreview :chartType="chartType"/>
            </div>
          </div>
        </el-form-item>

        <!-- 动态配置 -->
        <div v-if="form.chart_type && form.dataset" class="chart-config">
          <el-divider content-position="left">图表配置</el-divider>

          <!-- 显示当前选中的数据集和可用字段 -->
          <div class="field-selection-info">
            <el-alert
              v-if="selectedDataset && datasetFields.length > 0"
              :title="`当前数据集: ${selectedDataset.name}`"
              type="info"
              :closable="false"
              show-icon>
              <template #default>
                <div>可用字段: {{ datasetFields.join(', ') }}</div>
                <div v-if="form.configuration.xField" style="margin-top: 5px;">
                  已选择: X轴 - {{ form.configuration.xField }}
                </div>
                <div v-if="form.configuration.yFields && form.configuration.yFields.length > 0"
                     style="margin-top: 5px;">
                  已选择: Y轴 - {{ form.configuration.yFields.join(', ') }}
                </div>
              </template>
            </el-alert>
            <el-alert
              v-else-if="selectedDataset"
              title="正在加载字段..."
              type="warning"
              :closable="false"
              show-icon>
            </el-alert>
          </div>


          <div v-if="selectedChartType?.name === '饼图'">
            <el-form-item label="名称字段" required>
              <el-select
                v-model="form.configuration.pieNameField"
                placeholder="请选择名称字段"
                style="width: 100%"
                clearable>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
            </el-form-item>

            <el-form-item label="数值字段" required>
              <el-select
                v-model="form.configuration.pieValueField"
                placeholder="请选择数值字段"
                style="width: 100%"
                clearable>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
            </el-form-item>
          </div>

          <div v-else-if="selectedChartType?.name === '折线图'">
            <el-form-item label="X轴字段" required>
              <el-select
                v-model="form.configuration.xField"
                placeholder="请选择X轴字段"
                style="width: 100%"
                clearable
                @change="onXFieldChange">
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
            </el-form-item>

            <el-form-item label="Y轴字段" required>
              <div class="multi-field-selector">
                <div class="field-list">
                  <div v-for="(yField, index) in form.configuration.yFields"
                       :key="index"
                       class="field-item">
                    <el-select
                      v-model="form.configuration.yFields[index]"
                      placeholder="请选择Y轴字段"
                      style="width: calc(100% - 40px)"
                      clearable>
                      <el-option
                        v-for="field in availableYFields"
                        :key="field"
                        :label="field"
                        :value="field"/>
                    </el-select>
                    <el-button
                      v-if="form.configuration.yFields.length > 1"
                      type="danger"
                      text
                      circle
                      size="small"
                      @click="removeYField(index)"
                      style="margin-left: 8px">
                      <i class="el-icon-delete"></i>
                    </el-button>
                  </div>
                </div>
                <el-button
                  type="primary"
                  text
                  @click="addYField"
                  :disabled="!canAddMoreYFields"
                  style="margin-top: 8px">
                  <i class="el-icon-plus"></i> 添加折线
                </el-button>
                <div v-if="form.configuration.yFields.length === 0"
                     style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
                  <i class="el-icon-warning"></i> 请至少选择一个Y轴字段
                </div>
                <div v-if="form.configuration.yFields.length >= 5"
                     style="color: #e6a23c; font-size: 12px; margin-top: 5px;">
                  <i class="el-icon-info"></i> 最多支持5条折线
                </div>
              </div>
            </el-form-item>

            <!-- 折线样式配置 -->
            <el-collapse v-if="form.configuration.yFields.length > 0" class="line-style-config">
              <el-collapse-item title="折线样式配置">
                <div v-for="(yField, index) in form.configuration.yFields"
                     :key="index"
                     class="line-style-item">
                  <h4>折线 {{ index + 1 }}: {{ yField || '未选择字段' }}</h4>
                  <el-row :gutter="16">
                    <el-col :span="6">
                      <el-form-item :label="`线条颜色`">
                        <el-color-picker
                          v-model="form.configuration.lineStyles[index].color"
                          :predefine="predefinedColors"/>
                      </el-form-item>
                    </el-col>
                    <el-col :span="6">
                      <el-form-item :label="`线条宽度`">
                        <el-input-number
                          v-model="form.configuration.lineStyles[index].width"
                          :min="1"
                          :max="5"
                          controls-position="right"/>
                      </el-form-item>
                    </el-col>
                    <el-col :span="6">
                      <el-form-item :label="`显示数据点`">
                        <el-switch
                          v-model="form.configuration.lineStyles[index].showSymbol"/>
                      </el-form-item>
                    </el-col>
                    <el-col :span="6">
                      <el-form-item :label="`Y轴位置`" v-if="form.configuration.yFields.length > 1">
                        <el-radio-group v-model="form.configuration.lineStyles[index].yAxisIndex">
                          <el-radio :label="0">左侧</el-radio>
                          <el-radio :label="1">右侧</el-radio>
                        </el-radio-group>
                      </el-form-item>
                      <div v-else style="color: #909399; font-size: 12px; padding-top: 8px;">
                        单折线使用左侧Y轴
                      </div>
                    </el-col>
                  </el-row>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
          <!-- 地图配置 -->
          <div v-else-if="selectedChartType?.name === '地图'" class="map-config">
            <el-form-item label="地区字段" required>
              <el-select
                v-model="form.configuration.mapRegionField"
                placeholder="请选择地区字段（如省份、城市）"
                style="width: 100%"
                clearable>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
              <div v-if="!form.configuration.mapRegionField"
                   style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
                <i class="el-icon-warning"></i> 请选择地区字段（用于地图区域显示）
              </div>
            </el-form-item>

            <el-form-item label="数值字段" required>
              <el-select
                v-model="form.configuration.mapValueField"
                placeholder="请选择数值字段"
                style="width: 100%"
                clearable>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
              <div v-if="!form.configuration.mapValueField"
                   style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
                <i class="el-icon-warning"></i> 请选择数值字段（用于地图颜色深浅）
              </div>
            </el-form-item>

            <!-- 地图样式配置保持不变 -->
            <el-collapse class="map-style-config">
              <el-collapse-item title="地图样式配置">
                <el-form-item label="地图类型">
                  <el-radio-group v-model="form.configuration.mapType">
                    <el-radio label="china">中国地图</el-radio>
                    <el-radio label="world" disabled>世界地图</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="允许缩放">
                  <el-switch v-model="form.configuration.mapRoam"/>
                </el-form-item>

                <el-form-item label="显示地区标签">
                  <el-switch v-model="form.configuration.mapShowLabel"/>
                </el-form-item>

                <el-form-item label="颜色方案">
                  <el-select v-model="form.configuration.mapColorScheme" style="width: 100%">
                    <el-option label="蓝红渐变" value="blue-red"/>
                    <el-option label="绿黄渐变" value="green-yellow"/>
                    <el-option label="紫粉渐变" value="purple-pink"/>
                  </el-select>
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
          </div>

          <div v-else-if="selectedChartType?.name === '雷达图'">
            <el-form-item label="类别字段" required>
              <el-select
                v-model="form.configuration.radarCategoryField"
                placeholder="请选择类别字段（如用户ID）"
                style="width: 100%"
                clearable>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
              <div v-if="!form.configuration.radarCategoryField"
                   style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
                <i class="el-icon-warning"></i> 请选择类别字段（用于区分不同的雷达图多边形）
              </div>
            </el-form-item>

            <el-form-item label="指标字段" required>
              <div class="multi-field-selector">
                <div class="field-list">
                  <div v-for="(indicatorField, index) in form.configuration.indicatorFields"
                       :key="index"
                       class="field-item">
                    <el-select
                      v-model="form.configuration.indicatorFields[index]"
                      placeholder="请选择指标字段"
                      style="width: calc(100% - 40px)"
                      clearable>
                      <el-option
                        v-for="field in availableIndicatorFields"
                        :key="field"
                        :label="field"
                        :value="field"/>
                    </el-select>
                    <el-button
                      v-if="form.configuration.indicatorFields.length > 1"
                      type="danger"
                      text
                      circle
                      size="small"
                      @click="removeIndicatorField(index)"
                      style="margin-left: 8px">
                      <i class="el-icon-delete"></i>
                    </el-button>
                  </div>
                </div>
                <el-button
                  type="primary"
                  text
                  @click="addIndicatorField"
                  :disabled="!canAddMoreIndicatorFields"
                  style="margin-top: 8px">
                  <i class="el-icon-plus"></i> 添加指标
                </el-button>
                <div v-if="form.configuration.indicatorFields.length === 0"
                     style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
                  <i class="el-icon-warning"></i> 请至少选择一个指标字段
                </div>
                <div v-if="form.configuration.indicatorFields.length >= 8"
                     style="color: #e6a23c; font-size: 12px; margin-top: 5px;">
                  <i class="el-icon-info"></i> 最多支持8个指标
                </div>
              </div>
            </el-form-item>

            <!-- 添加雷达图形状配置 -->
            <el-form-item label="雷达图形状">
              <el-radio-group v-model="form.configuration.radarShape">
                <el-radio label="polygon">多边形</el-radio>
                <el-radio label="circle">圆形</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 雷达图样式配置 -->
            <el-collapse class="radar-style-config">
              <el-collapse-item title="雷达图样式配置">
                <el-form-item label="显示面积">
                  <el-switch v-model="form.configuration.radarShowArea"/>
                </el-form-item>

                <el-form-item label="显示数据点">
                  <el-switch v-model="form.configuration.radarShowSymbol"/>
                </el-form-item>

                <el-form-item label="显示数据标签">
                  <el-switch v-model="form.configuration.radarShowLabel"/>
                </el-form-item>

                <el-form-item label="分割段数">
                  <el-input-number
                    v-model="form.configuration.radarSplitNumber"
                    :min="3"
                    :max="10"
                    controls-position="right"
                    style="width: 100%"/>
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
          </div>

          <div v-else>
            <el-form-item label="X轴字段" required>
              <el-select
                v-model="form.configuration.xField"
                placeholder="请选择X轴字段"
                style="width: 100%"
                clearable>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
              <div v-if="!form.configuration.xField"
                   style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
                <i class="el-icon-warning"></i> 请选择X轴字段
              </div>
            </el-form-item>

            <el-form-item label="Y轴字段" required>
              <el-select
                v-model="form.configuration.yField"
                placeholder="请选择Y轴字段"
                style="width: 100%"
                clearable>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
              <div v-if="!form.configuration.yField"
                   style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
                <i class="el-icon-warning"></i> 请选择Y轴字段
              </div>
            </el-form-item>

            <el-form-item label="分组字段">
              <el-select
                v-model="form.configuration.group_by"
                placeholder="请选择分组字段（可选）"
                style="width: 100%"
                clearable>
                <el-option label="无分组" value=""/>
                <el-option
                  v-for="field in datasetFields"
                  :key="field"
                  :label="field"
                  :value="field"/>
              </el-select>
            </el-form-item>
          </div>

          <el-form-item label="图表标题">
            <el-input v-model="form.configuration.title" placeholder="请输入图表标题"/>
          </el-form-item>
          <!-- 折线图特定配置 -->
          <div v-if="selectedChartType?.name === '折线图'">
            <el-form-item label="平滑曲线">
              <el-switch v-model="form.configuration.lineSmooth"/>
            </el-form-item>

            <el-form-item label="显示面积">
              <el-switch v-model="form.configuration.lineAreaStyle"/>
            </el-form-item>

            <el-form-item label="显示数据标签">
              <el-switch v-model="form.configuration.lineShowLabel"/>
            </el-form-item>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看图表对话框 -->
    <el-dialog
      title="查看图表"
      v-model="showViewDialog"
      width="95%"
      top="2vh"
      class="chart-view-dialog"
      @close="currentVisualization = null">

      <div v-if="currentVisualization" class="chart-view-container">
        <div class="chart-view-header">
          <div class="header-content">
            <h2>{{ currentVisualization.name }}</h2>
            <p v-if="currentVisualization.description" class="chart-description">
              {{ currentVisualization.description }}
            </p>
            <div class="chart-meta">
              <el-tag :type="getChartTypeTagType(currentVisualization.chart_type_name)"
                      size="large">
                {{ currentVisualization.chart_type_name }}
              </el-tag>
              <el-tag type="info" size="large">
                数据集: {{
                  getDatasetName(currentVisualization.dataset) || currentVisualization.dataset_name
                }}
              </el-tag>
              <el-tag type="success" size="large">
                创建时间: {{ formatDate(currentVisualization.created_at) }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="chart-view-content">
          <div class="chart-wrapper" v-loading="chartLoading"
               element-loading-text="正在加载图表数据..."
               element-loading-background="rgba(255, 255, 255, 0.8)">
            <!-- 调试信息 -->
            <div v-if="chartLoading" class="loading-state">
              <el-icon class="is-loading" color="#409EFF">
                <Loading/>
              </el-icon>
              <p>图表数据加载中...</p>
            </div>

            <!-- 根据图表类型显示不同的组件 -->
            <div class="chart-content" v-if="!chartLoading">
              <BarChart
                v-if="currentVisualization.chart_type_name === '柱状图'"
                :data="chartData"
                :config="currentVisualization.configuration"/>

              <LineChart
                v-else-if="currentVisualization.chart_type_name === '折线图'"
                :data="chartData"
                :config="currentVisualization.configuration"/>

              <PieChart
                v-else-if="currentVisualization.chart_type_name === '饼图'"
                :data="chartData"
                :config="currentVisualization.configuration"/>

              <ScatterChart
                v-else-if="currentVisualization.chart_type_name === '散点图'"
                :data="chartData"
                :config="currentVisualization.configuration"/>

              <RadarChart
                v-else-if="currentVisualization.chart_type_name === '雷达图'"
                :data="chartData"
                :config="currentVisualization.configuration"/>

              <MapChart
                v-else-if="currentVisualization.chart_type_name === '地图'"
                :data="chartData"
                :config="currentVisualization.configuration"/>

              <div v-else class="no-chart-support">
                <el-empty description="不支持的图表类型">
                  <p>当前图表类型 "{{ currentVisualization.chart_type_name }}" 暂不支持显示</p>
                </el-empty>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted, nextTick, computed, watch, defineAsyncComponent} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {visualizationAPI} from '../api/visualization'
import {datasetsAPI} from '../api/datasets'
import ChartPreview from '../components/charts/ChartPreview.vue'

// 简化组件导入 - 使用条件导入避免错误
let BarChart, LineChart, PieChart, ScatterChart, RadarChart, MapChart

// 尝试导入组件，如果失败则使用占位组件
const loadChartComponent = async (componentPath, componentName) => {
  try {
    const module = await import(/* @vite-ignore */ componentPath)
    return module.default
  } catch (error) {
    console.warn(`${componentName} 组件加载失败:`, error)
    return {
      template: `
        <div class="chart-error">
          <i class="el-icon-warning"></i>
          <p>${componentName}组件加载失败</p>
        </div>
      `,
      props: ['data', 'config']
    }
  }
}

const getDatasetName = (datasetId) => {
  if (!datasetId) return ''
  const dataset = datasets.value.find(ds => ds.id === datasetId)
  return dataset?.name || ''
}

// 在 Visualization.vue 的 script 部分添加
const getChartTypeTagType = (chartTypeName) => {
  const typeMap = {
    '柱状图': 'primary',
    '折线图': 'success',
    '饼图': 'warning',
    '散点图': 'info',
    '雷达图': 'danger',
    '地图': 'success'
  }
  return typeMap[chartTypeName] || 'info'
}

const getChartTypeIcon = (chartTypeName) => {
  const iconMap = {
    '柱状图': 'el-icon-data-board',
    '折线图': 'el-icon-data-line',
    '饼图': 'el-icon-pie-chart',
    '散点图': 'el-icon-odometer',
    '雷达图': 'el-icon-star-off',
    '地图': 'el-icon-map-location'
  }
  return iconMap[chartTypeName] || 'el-icon-data-analysis'
}

const getChartTypeClass = (chartTypeName) => {
  const classMap = {
    '柱状图': 'mini-bar',
    '折线图': 'mini-line',
    '饼图': 'mini-pie',
    '散点图': 'mini-scatter',
    '雷达图': 'mini-radar',
    '地图': 'mini-map'
  }
  return classMap[chartTypeName] || 'mini-default'
}
const availableIndicatorFields = computed(() => {
  // 排除已选择的类别字段
  return datasetFields.value.filter(field => field !== form.configuration.categoryField)
})
const addIndicatorField = () => {
  if (form.configuration.indicatorFields.length >= 8) {
    ElMessage.warning('最多只能添加8个指标')
    return
  }

  form.configuration.indicatorFields.push('')
  ElMessage.info(`已添加第 ${form.configuration.indicatorFields.length} 个指标`)
}

const removeIndicatorField = (index) => {
  if (form.configuration.indicatorFields.length <= 1) {
    ElMessage.warning('至少需要保留一个指标')
    return
  }

  form.configuration.indicatorFields.splice(index, 1)
  ElMessage.info('已移除指标')
}

const canAddMoreIndicatorFields = computed(() => {
  // 添加安全检查，确保 indicatorFields 存在
  if (!form.configuration.indicatorFields) {
    return true // 如果不存在，默认可以添加
  }
  return form.configuration.indicatorFields.length < 8
})
const selectChartType = (chartType) => {
  console.log('🎯 选择图表类型:', chartType)

  if (!chartType || !chartType.id) {
    ElMessage.warning('无效的图表类型')
    return
  }

  // 设置选中的图表类型
  form.chart_type = chartType.id

  // 如果已经选择了数据集，自动推荐字段
  if (form.dataset && datasetFields.value.length > 0) {
    // 延迟执行以确保表单已更新
    nextTick(() => {
      autoRecommendFields()
    })
  }

  ElMessage.success(`已选择: ${chartType.name}`)
}

const handleDropdownCommand = (command, viz) => {
  switch (command) {
    case 'view':
      viewVisualization(viz.id)
      break
    case 'edit':
      editVisualization(viz)
      break
    case 'delete':
      deleteVisualization(viz.id)
      break
  }
}

// 初始化组件
const initializeComponents = async () => {
  BarChart = await loadChartComponent('../components/charts/BarChart.vue', '柱状图')
  LineChart = await loadChartComponent('../components/charts/LineChart.vue', '折线图')
  PieChart = await loadChartComponent('../components/charts/PieChart.vue', '饼图')
  ScatterChart = await loadChartComponent('../components/charts/ScatterChart.vue', '散点图')
  RadarChart = await loadChartComponent('../components/charts/RadarChart.vue', '雷达图')
  MapChart = await loadChartComponent('../components/charts/MapChart.vue', '地图') // 添加地图组件导入
}

// 调用初始化
initializeComponents()

// 响应式数据
const visualizations = ref([])
const chartTypes = ref([])
const datasets = ref([])
const datasetFieldsMap = ref({})
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const loading = ref(false)
const chartLoading = ref(false)
const isEditing = ref(false)
const currentVisualization = ref(null)
const chartData = ref({})
const formRef = ref()

// 预定义颜色数组
const predefinedColors = [
  '#5470c6',
  '#91cc75',
  '#fac858',
  '#ee6666',
  '#73c0de',
  '#3ba272',
  '#fc8452',
  '#9a60b4',
  '#ea7ccc'
]

// 表单数据
const form = reactive({
  id: null,
  name: '',
  description: '',
  dataset: '',
  chart_type: '',
  configuration: {
    // 通用字段
    xField: '',
    yField: '', // 单Y轴字段（柱状图、散点图等）
    yFields: [''], // 多Y轴字段数组（折线图）
    indicatorFields: [''], // 雷达图指标字段数组
    group_by: '',
    title: '',

    // 饼图特定字段
    pieNameField: '',      // 饼图名称字段
    pieValueField: '',     // 饼图数值字段

    // 地图特定字段
    mapRegionField: '',    // 地图地区字段
    mapValueField: '',     // 地图数值字段
    mapType: 'china',
    mapRoam: true,
    mapShowLabel: true,
    mapColorScheme: 'blue-red',

    // 雷达图特定字段
    radarCategoryField: '', // 雷达图类别字段

    // 样式配置
    // 折线图样式
    lineSmooth: false,
    lineAreaStyle: false,
    lineShowLabel: false,
    lineStyles: [{
      color: predefinedColors[0],
      width: 2,
      showSymbol: true
    }],

    // 雷达图样式
    radarShape: 'polygon',
    radarSplitNumber: 4,
    radarShowArea: true,
    radarShowSymbol: true,
    radarShowLabel: false
  }
})

// 计算属性
const selectedChartType = computed(() => {
  return chartTypes.value.find(type => type.id === form.chart_type)
})

const selectedDataset = computed(() => {
  return datasets.value.find(ds => ds.id === form.dataset)
})

const datasetFields = computed(() => {
  if (!form.dataset) return []
  return datasetFieldsMap.value[form.dataset] || []
})

const availableYFields = computed(() => {
  // 排除已选择的X轴字段
  return datasetFields.value.filter(field => field !== form.configuration.xField)
})

const canAddMoreYFields = computed(() => {
  return form.configuration.yFields.length < 5
})

// 表单验证规则
const rules = reactive({
  name: [{required: true, message: '请输入图表名称', trigger: 'blur'}],
  dataset: [{required: true, message: '请选择数据集', trigger: 'change'}],
  chart_type: [{required: true, message: '请选择图表类型', trigger: 'change'}]
})

// 方法
const addYField = () => {
  if (form.configuration.yFields.length >= 5) {
    ElMessage.warning('最多只能添加5条折线')
    return
  }

  form.configuration.yFields.push('')

  // 添加对应的样式配置
  const colorIndex = form.configuration.yFields.length - 1
  form.configuration.lineStyles.push({
    color: predefinedColors[colorIndex % predefinedColors.length],
    width: 2,
    showSymbol: true
  })

  ElMessage.info(`已添加第 ${form.configuration.yFields.length} 条折线`)
}

const removeYField = (index) => {
  if (form.configuration.yFields.length <= 1) {
    ElMessage.warning('至少需要保留一条折线')
    return
  }

  form.configuration.yFields.splice(index, 1)
  form.configuration.lineStyles.splice(index, 1)

  ElMessage.info('已移除折线')
}

const onXFieldChange = () => {
  // 当X轴字段改变时，清空Y轴字段选择
  if (form.configuration.yFields.length > 0) {
    form.configuration.yFields = ['']
    form.configuration.lineStyles = [{
      color: predefinedColors[0],
      width: 2,
      showSymbol: true
    }]
  }
}

// 自动推荐字段函数
const autoRecommendFields = () => {
  if (!form.chart_type || !form.dataset || datasetFields.value.length === 0) {
    return
  }

  const chartType = selectedChartType.value
  if (!chartType) return

  console.log('🤖 自动推荐字段，图表类型:', chartType.name)

  const categoryCandidates = []
  const numericCandidates = []
  const otherFields = []

  datasetFields.value.forEach(field => {
    const fieldStr = String(field).toLowerCase()

    if (fieldStr.match(/(名称|名字|类别|分类|类型|日期|时间|地区|城市|省份|状态|阶段|等级|name|category|type|date|time|region|city|status|stage|level)/)) {
      categoryCandidates.push(field)
    } else if (fieldStr.match(/(数值|数量|金额|价格|销量|收入|值|价值|分数|评分|value|amount|price|count|total|sum|score|rating)/)) {
      numericCandidates.push(field)
    } else {
      otherFields.push(field)
    }
  })

  let defaultCategory = categoryCandidates[0]
  let defaultNumerics = numericCandidates.slice(0, 4)

  if (!defaultCategory && otherFields.length > 0) {
    defaultCategory = otherFields[0]
  } else if (!defaultCategory && datasetFields.value.length > 0) {
    defaultCategory = datasetFields.value[0]
  }

  // 如果没有足够的数值字段，补充其他字段
  while (defaultNumerics.length < 4 && otherFields.length > 0) {
    const otherField = otherFields.shift()
    if (otherField && otherField !== defaultCategory) {
      defaultNumerics.push(otherField)
    }
  }

  if (chartType.name === '饼图') {
    if (!form.configuration.pieNameField && defaultCategory) {
      form.configuration.pieNameField = defaultCategory
    }
    if (!form.configuration.pieValueField && defaultNumerics[0]) {
      form.configuration.pieValueField = defaultNumerics[0]
    }
  } else if (chartType.name === '折线图') {
    if (!form.configuration.xField && defaultCategory) {
      form.configuration.xField = defaultCategory
    }
    if (form.configuration.yFields.length === 1 && !form.configuration.yFields[0]) {
      form.configuration.yFields = defaultNumerics
      form.configuration.lineStyles = defaultNumerics.map((field, index) => ({
        color: predefinedColors[index % predefinedColors.length],
        width: 2,
        showSymbol: true,
        yAxisIndex: index
      }))
    }
  } else if (chartType.name === '雷达图') {
    if (!form.configuration.radarCategoryField && defaultCategory) {
      form.configuration.radarCategoryField = defaultCategory
    }
    if (form.configuration.indicatorFields.length === 1 && !form.configuration.indicatorFields[0]) {
      form.configuration.indicatorFields = defaultNumerics.slice(0, 4)
    }
  } else if (chartType.name === '地图') {
    if (!form.configuration.mapRegionField && defaultCategory) {
      form.configuration.mapRegionField = defaultCategory
    }
    if (!form.configuration.mapValueField && defaultNumerics[0]) {
      form.configuration.mapValueField = defaultNumerics[0]
    }
  } else {
    // 柱状图、散点图等
    if (!form.configuration.xField && defaultCategory) {
      form.configuration.xField = defaultCategory
    }
    if (!form.configuration.yField && defaultNumerics[0]) {
      form.configuration.yField = defaultNumerics[0]
    }
  }
}

const loadData = async () => {
  try {
    loading.value = true
    console.log('🚀 开始加载数据...')

    const datasetsRes = await datasetsAPI.getDatasets()
    console.log('📊 数据集完整响应:', datasetsRes)

    // 直接使用数组响应
    datasets.value = Array.isArray(datasetsRes) ? datasetsRes :
      Array.isArray(datasetsRes?.data) ? datasetsRes.data : []

    console.log('🎯 最终数据集:', datasets.value)

    if (datasets.value.length > 0) {
      ElMessage.success(`成功加载 ${datasets.value.length} 个数据集`)
    }

    // 同时加载其他数据
    try {
      const [vizRes, typesRes] = await Promise.all([
        visualizationAPI.getVisualizations(),
        visualizationAPI.getChartTypes()
      ])

      console.log('📈 可视化原始响应:', vizRes)
      console.log('📊 图表类型原始响应:', typesRes)

      // 修复可视化数据处理
      visualizations.value = Array.isArray(vizRes) ? vizRes :
        Array.isArray(vizRes?.data) ? vizRes.data :
          Array.isArray(vizRes?.results) ? vizRes.results : []

      // 修复图表类型数据处理
      chartTypes.value = Array.isArray(typesRes) ? typesRes :
        Array.isArray(typesRes?.data) ? typesRes.data :
          Array.isArray(typesRes?.results) ? typesRes.results : []

      console.log('📈 处理后的可视化数量:', visualizations.value.length)
      console.log('📊 处理后的图表类型数量:', chartTypes.value.length)
      console.log('📈 第一个可视化:', visualizations.value[0])

    } catch (otherError) {
      console.error('加载其他数据失败:', otherError)
    }

  } catch (error) {
    console.error('❌ 加载失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadDatasetFields = async (datasetId) => {
  if (!datasetId) return []

  try {
    console.log('🔍 加载数据集字段，数据集ID:', datasetId)

    // 如果已经有缓存的字段，直接返回
    if (datasetFieldsMap.value[datasetId]) {
      console.log('✅ 使用缓存的字段:', datasetFieldsMap.value[datasetId])
      return datasetFieldsMap.value[datasetId]
    }

    let fields = []

    try {
      // 方法1: 使用专门的API获取字段
      console.log('🔄 尝试使用可视化API获取字段...')
      const response = await visualizationAPI.getDatasetColumns(datasetId)
      console.log('📊 字段API完整响应:', response)

      // 根据你的控制台输出，正确的格式是 {columns: Array(2)}
      if (response.data && response.data.columns) {
        fields = response.data.columns
        console.log('✅ 从API成功获取字段:', fields)
      } else {
        // 如果格式不对，但响应中有columns字段
        if (response.columns) {
          fields = response.columns
          console.log('✅ 从response.columns获取字段:', fields)
        } else {
          throw new Error('API返回的字段格式不正确')
        }
      }

    } catch (apiError) {
      console.warn('❌ 可视化API获取字段失败，尝试备用方法:', apiError)

      // 方法2: 回退到从数据集数据中提取字段
      try {
        console.log('🔄 尝试备用方法：从数据集数据提取字段...')
        const dataRes = await datasetsAPI.getDatasetData(datasetId)
        console.log('📊 数据集数据完整响应:', dataRes)

        // 根据你的控制台输出，正确的记录路径是: dataRes.records
        const records = dataRes.records || dataRes.data?.records || []
        console.log('📋 提取的记录数量:', records.length)

        if (records.length > 0) {
          const firstRecord = records[0]
          console.log('📝 第一条记录详情:', firstRecord)

          // 根据你的控制台输出，记录格式是: { data: { 卖场名称: "...", 销售金额: ... } }
          if (firstRecord.data && typeof firstRecord.data === 'object') {
            fields = Object.keys(firstRecord.data)
            console.log('🎯 从data字段提取字段:', fields)
          }
        }
      } catch (dataError) {
        console.error('❌ 备用方法也失败:', dataError)
      }
    }

    // 如果还是没获取到字段，使用默认字段
    if (fields.length === 0) {
      console.warn('⚠️ 无法获取字段，使用默认字段')
      fields = ['id', '名称', '数值', '类别', '日期', '数量', '价格', '计数']
    }

    console.log('✅ 最终字段列表:', fields)
    datasetFieldsMap.value[datasetId] = fields
    return fields

  } catch (error) {
    console.error('❌ 加载数据集字段失败:', error)
    const defaultFields = ['id', '名称', '数值', '类别', '日期', '数量']
    datasetFieldsMap.value[datasetId] = defaultFields
    return defaultFields
  }
}

const onDatasetChange = async (datasetId) => {
  console.log('🔄 数据集变更:', datasetId)

  if (datasetId) {
    try {
      // 重置配置
      form.configuration.xField = ''
      form.configuration.yField = ''
      form.configuration.nameField = ''
      form.configuration.valueField = ''
      form.configuration.group_by = ''

      // 加载数据集字段
      const fields = await loadDatasetFields(datasetId)
      console.log('✅ 加载到的字段:', fields)

      if (fields.length > 0) {
        // 更智能的字段推荐
        const categoryCandidates = []
        const numericCandidates = []
        const otherFields = []

        fields.forEach(field => {
          const fieldStr = String(field).toLowerCase()

          // 分类字段（用于X轴或名称）
          if (fieldStr.match(/(名称|名字|类别|分类|类型|日期|时间|地区|城市|省份|状态|阶段|等级|name|category|type|date|time|region|city|status|stage|level)/)) {
            categoryCandidates.push(field)
          }
          // 数值字段（用于Y轴或数值）
          else if (fieldStr.match(/(数值|数量|金额|价格|销量|收入|值|价值|分数|评分|value|amount|price|count|total|sum|score|rating)/)) {
            numericCandidates.push(field)
          } else {
            otherFields.push(field)
          }
        })

        // 优先使用明确的分类和数值字段
        let defaultCategory = categoryCandidates[0]
        let defaultNumeric = numericCandidates[0]

        // 如果没有明确的分类字段，使用其他字段
        if (!defaultCategory && otherFields.length > 0) {
          defaultCategory = otherFields[0]
        } else if (!defaultCategory && fields.length > 0) {
          defaultCategory = fields[0]
        }

        // 如果没有明确的数值字段，使用其他字段
        if (!defaultNumeric && otherFields.length > 0) {
          defaultNumeric = otherFields.find(field => field !== defaultCategory) || otherFields[0]
        } else if (!defaultNumeric && fields.length > 1) {
          defaultNumeric = fields.find(field => field !== defaultCategory) || fields[1] || fields[0]
        } else if (!defaultNumeric) {
          defaultNumeric = defaultCategory
        }

        // 根据图表类型设置字段
        if (selectedChartType.value?.name === '饼图') {
          form.configuration.nameField = defaultCategory
          form.configuration.valueField = defaultNumeric
        } else {
          form.configuration.xField = defaultCategory
          form.configuration.yField = defaultNumeric
        }

        console.log('🤖 智能字段推荐结果:', {
          分类字段候选: categoryCandidates,
          数值字段候选: numericCandidates,
          其他字段: otherFields,
          最终分类字段: defaultCategory,
          最终数值字段: defaultNumeric
        })

        if (defaultCategory && defaultNumeric) {
          ElMessage.success(`已自动选择字段: ${defaultCategory}, ${defaultNumeric}`)
        }
      }

    } catch (error) {
      console.error('❌ 处理数据集变更失败:', error)
      ElMessage.warning('数据集字段加载失败，请手动选择字段')
    }
  }
}

const submitForm = async () => {
  if (!formRef.value) return

  try {
    // 手动验证必要字段
    if (!form.name.trim()) {
      ElMessage.warning('请输入图表名称')
      return
    }
    if (!form.dataset) {
      ElMessage.warning('请选择数据集')
      return
    }
    if (!form.chart_type) {
      ElMessage.warning('请选择图表类型')
      return
    }

    // 根据图表类型验证配置字段
    const chartType = selectedChartType.value
    if (chartType) {
      if (chartType.name === '饼图') {
        if (!form.configuration.pieNameField || !form.configuration.pieValueField) {
          ElMessage.warning('饼图需要选择名称字段和数值字段')
          return
        }
      } else if (chartType.name === '折线图') {
        if (!form.configuration.xField) {
          ElMessage.warning('请选择X轴字段')
          return
        }
        const validYFields = form.configuration.yFields.filter(field => field && field.trim())
        if (validYFields.length === 0) {
          ElMessage.warning('请至少选择一个有效的Y轴字段')
          return
        }
      } else if (chartType.name === '雷达图') {
        if (!form.configuration.radarCategoryField) {
          ElMessage.warning('请选择类别字段')
          return
        }
        const validIndicatorFields = form.configuration.indicatorFields.filter(field => field && field.trim())
        if (validIndicatorFields.length === 0) {
          ElMessage.warning('请至少选择一个有效的指标字段')
          return
        }
      } else if (chartType.name === '地图') {
        if (!form.configuration.mapRegionField || !form.configuration.mapValueField) {
          ElMessage.warning('地图需要选择地区字段和数值字段')
          return
        }
      } else {
        if (!form.configuration.xField || !form.configuration.yField) {
          ElMessage.warning('请选择X轴和Y轴字段')
          return
        }
      }
    }

    loading.value = true

    // 构建基础配置
    const submitData = {
      name: form.name,
      description: form.description,
      dataset: form.dataset,
      chart_type: form.chart_type,
      configuration: {
        // 通用配置
        xField: form.configuration.xField,
        yField: form.configuration.yField,
        group_by: form.configuration.group_by,
        title: form.configuration.title
      }
    }

    // 根据图表类型添加特定配置
    const currentChartType = selectedChartType.value?.name

    if (currentChartType === '折线图') {
      submitData.configuration.yFields = form.configuration.yFields.filter(field => field && field.trim())
      submitData.configuration.smooth = form.configuration.lineSmooth
      submitData.configuration.areaStyle = form.configuration.lineAreaStyle
      submitData.configuration.lineShowLabel = form.configuration.lineShowLabel
      submitData.configuration.lineStyles = form.configuration.lineStyles
    } else if (currentChartType === '雷达图') {
      submitData.configuration.categoryField = form.configuration.radarCategoryField
      submitData.configuration.indicatorFields = form.configuration.indicatorFields.filter(field => field && field.trim())
      submitData.configuration.radarShape = form.configuration.radarShape
      submitData.configuration.radarSplitNumber = form.configuration.radarSplitNumber
      submitData.configuration.radarShowArea = form.configuration.radarShowArea
      submitData.configuration.radarShowSymbol = form.configuration.radarShowSymbol
      submitData.configuration.radarShowLabel = form.configuration.radarShowLabel
    } else if (currentChartType === '饼图') {
      submitData.configuration.nameField = form.configuration.pieNameField
      submitData.configuration.valueField = form.configuration.pieValueField
    } else if (currentChartType === '地图') {
      submitData.configuration.regionField = form.configuration.mapRegionField
      submitData.configuration.valueField = form.configuration.mapValueField
      submitData.configuration.mapType = form.configuration.mapType
      submitData.configuration.mapRoam = form.configuration.mapRoam
      submitData.configuration.mapShowLabel = form.configuration.mapShowLabel
      submitData.configuration.mapColorScheme = form.configuration.mapColorScheme
    }

    console.log('📤 提交数据:', JSON.stringify(submitData, null, 2))

    if (isEditing.value) {
      await visualizationAPI.updateVisualization(form.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await visualizationAPI.createVisualization(submitData)
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    await loadData()

  } catch (error) {
    console.error('❌ 提交失败:', error)
    ElMessage.error(isEditing.value ? '更新失败' : '创建失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const viewVisualization = async (id) => {
  try {
    chartLoading.value = true

    console.log('🔍 查看图表 ID:', id)

    // 直接从当前的可视化列表中查找
    const visualization = visualizations.value.find(viz => viz.id === id)

    if (!visualization) {
      ElMessage.error('未找到对应的可视化图表')
      chartLoading.value = false
      return
    }

    currentVisualization.value = visualization

    console.log('📋 可视化配置:', visualization.configuration)

    // 获取图表数据
    const dataRes = await visualizationAPI.getVisualizationData(id)
    console.log('📈 图表数据完整响应:', dataRes)

    // 处理不同的响应格式
    let rawChartData = dataRes?.data || dataRes

    console.log('📊 原始图表数据:', rawChartData)
    console.log('📊 图表类型:', visualization.chart_type_name)
    console.log('📊 响应状态:', dataRes?.status)
    console.log('📊 响应消息:', dataRes?.message)

    // 统一数据格式处理
    if (rawChartData && typeof rawChartData === 'object') {
      // 如果数据在 data 字段中
      if (rawChartData.data !== undefined) {
        chartData.value = rawChartData.data
        console.log('✅ 从 data 字段获取数据:', chartData.value)
      } else {
        // 如果数据直接就是数组或对象
        chartData.value = rawChartData
        console.log('✅ 直接使用原始数据:', chartData.value)
      }
    } else {
      chartData.value = rawChartData || {}
      console.log('⚠️ 使用默认空数据')
    }

    console.log('🎯 最终设置的图表数据:', chartData.value)
    console.log('🎯 数据类型:', typeof chartData.value)
    console.log('🎯 是否为数组:', Array.isArray(chartData.value))
    console.log('🎯 数据长度:', Array.isArray(chartData.value) ? chartData.value.length : '非数组')

    // 检查数据是否真的为空
    const isEmptyData = Array.isArray(chartData.value) ?
                       chartData.value.length === 0 :
                       Object.keys(chartData.value).length === 0

    console.log('📊 数据是否为空:', isEmptyData)

    if (!isEmptyData) {
      await nextTick()
      showViewDialog.value = true
      ElMessage.success('图表数据加载成功')
    } else {
      console.warn('⚠️ 数据为空或格式不正确，但仍然显示图表')

      // 显示测试数据用于调试
      if (visualization.chart_type_name === '地图') {
        console.log('🗺️ 使用测试地图数据')
        chartData.value = [
          { name: '北京市', value: 100 },
          { name: '上海市', value: 80 },
          { name: '广东省', value: 120 },
          { name: '江苏省', value: 90 },
          { name: '浙江省', value: 70 }
        ]
      }

      await nextTick()
      showViewDialog.value = true
      ElMessage.info('图表数据为空，显示测试数据')
    }

    setTimeout(() => {
      chartLoading.value = false
    }, 1000)

  } catch (error) {
    console.error('❌ 查看图表失败:', error)
    ElMessage.error('加载图表数据失败: ' + (error.message || '未知错误'))
    chartLoading.value = false
  }
}

// 新增：根据图表类型验证数据
const validateChartData = (data, chartType) => {
  if (!data) return false

  switch (chartType) {
    case '柱状图':
    case '折线图':
      return data.categories && data.series && Array.isArray(data.categories) && Array.isArray(data.series)

    case '饼图':
      return data.data && Array.isArray(data.data)

    case '散点图':
      return data.data && Array.isArray(data.data)

    case '雷达图':
      return data.indicators && data.series && Array.isArray(data.indicators) && Array.isArray(data.series)

    case '地图':
      // 地图数据可以是空数组，只要有 data 字段就行
      return data.data !== undefined && Array.isArray(data.data)

    default:
      return data !== null && typeof data === 'object'
  }
}
const editVisualization = async (viz) => {
  try {
    isEditing.value = true

    // 处理配置数据的兼容性
    const config = {...viz.configuration}

    // 确保 yFields 和 lineStyles 存在
    if (!config.yFields) {
      config.yFields = config.yField ? [config.yField] : ['']
    }
    if (!config.lineStyles) {
      config.lineStyles = config.yFields.map((field, index) => ({
        color: predefinedColors[index % predefinedColors.length],
        width: 2,
        showSymbol: true,
        yAxisIndex: index
      }))
    } else {
      // 确保现有的lineStyles都有yAxisIndex
      config.lineStyles = config.lineStyles.map((style, index) => ({
        ...style,
        yAxisIndex: style.yAxisIndex !== undefined ? style.yAxisIndex : index
      }))
    }

    // 确保雷达图配置存在（兼容旧数据）
    if (!config.categoryField) {
      config.categoryField = config.xField || ''
    }
    if (!config.indicatorFields) {
      config.indicatorFields = config.yField ? [config.yField] : ['']
    }

    // 兼容性处理：将旧的配置字段映射到新的字段名
    // 折线图配置兼容
    if (config.smooth !== undefined && config.lineSmooth === undefined) {
      config.lineSmooth = config.smooth
    }
    if (config.areaStyle !== undefined && config.lineAreaStyle === undefined) {
      config.lineAreaStyle = config.areaStyle
    }
    if (config.showLabel !== undefined && config.lineShowLabel === undefined) {
      config.lineShowLabel = config.showLabel
    }

    // 雷达图配置兼容
    if (config.shape !== undefined && config.radarShape === undefined) {
      config.radarShape = config.shape
    }
    if (config.splitNumber !== undefined && config.radarSplitNumber === undefined) {
      config.radarSplitNumber = config.splitNumber
    }
    if (config.showArea !== undefined && config.radarShowArea === undefined) {
      config.radarShowArea = config.showArea
    }
    if (config.showSymbol !== undefined && config.radarShowSymbol === undefined) {
      config.radarShowSymbol = config.showSymbol
    }
    if (config.showLabel !== undefined && config.radarShowLabel === undefined) {
      config.radarShowLabel = config.showLabel
    }

    // 确保雷达图特定配置存在
    if (!config.radarShape) config.radarShape = 'polygon'
    if (!config.radarSplitNumber) config.radarSplitNumber = 4
    if (!config.radarShowArea) config.radarShowArea = true
    if (!config.radarShowSymbol) config.radarShowSymbol = true
    if (!config.radarShowLabel) config.radarShowLabel = false

    // 确保折线图特定配置存在
    if (!config.lineSmooth) config.lineSmooth = false
    if (!config.lineAreaStyle) config.lineAreaStyle = false
    if (!config.lineShowLabel) config.lineShowLabel = false

    Object.assign(form, {
      id: viz.id,
      name: viz.name,
      description: viz.description,
      dataset: viz.dataset,
      chart_type: viz.chart_type,
      configuration: config
    })

    console.log('编辑可视化:', viz)

    // 加载数据集字段
    if (viz.dataset) {
      await loadDatasetFields(viz.dataset)
    }

    showCreateDialog.value = true
  } catch (error) {
    console.error('编辑失败:', error)
    ElMessage.error('编辑失败')
  }
}

const deleteVisualization = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除这个图表吗？此操作不可恢复。', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    await visualizationAPI.deleteVisualization(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {
    if (error === 'cancel') return
    console.error('删除失败:', error)
    ElMessage.error('删除失败: ' + (error.message || '未知错误'))
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  Object.assign(form, {
    id: null,
    name: '',
    description: '',
    dataset: '',
    chart_type: '',
    configuration: {
      // 通用字段
      xField: '',
      yField: '',
      yFields: [''],
      indicatorFields: [''],
      group_by: '',
      title: '',

      // 饼图特定字段
      pieNameField: '',
      pieValueField: '',

      // 地图特定字段
      mapRegionField: '',
      mapValueField: '',
      mapType: 'china',
      mapRoam: true,
      mapShowLabel: true,
      mapColorScheme: 'blue-red',

      // 雷达图特定字段
      radarCategoryField: '',

      // 样式配置
      lineSmooth: false,
      lineAreaStyle: false,
      lineShowLabel: false,
      lineStyles: [{
        color: predefinedColors[0],
        width: 2,
        showSymbol: true,
        yAxisIndex: 0
      }],

      radarShape: 'polygon',
      radarSplitNumber: 4,
      radarShowArea: true,
      radarShowSymbol: true,
      radarShowLabel: false
    }
  })
  isEditing.value = false
}
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 监听
watch(showViewDialog, (newVal) => {
  if (!newVal) {
    // 对话框关闭时清理数据
    currentVisualization.value = null
    chartData.value = {}
  }
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.visualization-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 添加地图样式 */
.mini-map {
  background: linear-gradient(135deg, #5470c6, #73c0de);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.data-stats {
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.visualization-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.viz-card {
  transition: all 0.3s ease;
  border: 1px solid #e6e8eb;
}

.viz-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0;
}

.card-title {
  flex: 1;
}

.card-title h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
  line-height: 1.4;
}

.viz-content {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.viz-info {
  flex: 1;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.info-item i {
  margin-right: 8px;
  color: #909399;
  width: 16px;
}

.description {
  color: #909399;
  font-style: italic;
}

.viz-preview {
  width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-chart {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.mini-bar {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.mini-line {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.mini-pie {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
}

.mini-scatter {
  background: linear-gradient(135deg, #909399, #a6a9ad);
}

.mini-radar {
  background: linear-gradient(135deg, #F56C6C, #f78989);
}

.mini-default {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.loading-state, .empty-state {
  margin: 40px 0;
}

.chart-type-selector {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.chart-type-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-type-card.selected {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.chart-config {
  border-top: 1px solid #e1e5e9;
  padding-top: 16px;
  margin-top: 16px;
}

.chart-view-container {
  height: 80vh;
  display: flex;
  flex-direction: column;
  background: white;
}

.chart-view-header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 24px;
}

.chart-view-header .header-content {
  max-width: 100%;
}

.chart-view-header .header-content h2 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.3;
}

.chart-view-header .header-content .chart-description {
  margin: 0 0 16px 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
}

.chart-view-header .header-content .chart-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-view-header .header-content .chart-meta .el-tag {
  font-weight: 500;
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-view-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.chart-view-header p {
  margin: 0 0 12px 0;
  color: #606266;
}

.chart-meta {
  display: flex;
  gap: 8px;
}

.chart-view-content {
  flex: 1;
  display: flex;
  /* 重要：防止内容溢出 */
  min-height: 0;
}

.chart-container {
  flex: 1;
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  min-height: 400px;
  position: relative;
}

.chart-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  position: relative;
  min-height: 0;
}

.chart-wrapper .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #409EFF;
}

.chart-wrapper .loading-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: rotating 2s linear infinite;
}

.chart-wrapper .loading-state p {
  margin: 0;
  font-size: 16px;
  color: #6b7280;
}

.chart-content {
  flex: 1;
  display: flex;
  min-height: 0;
  padding: 20px;
}

/* 确保所有图表组件都填满容器 */
.chart-content > * {
  flex: 1;
  min-height: 0;
}

.no-chart-support {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f9fafb;
  border-radius: 8px;
}

.no-chart-support .el-empty {
  padding: 40px;
}

.no-chart-support .el-empty .el-empty__description p {
  margin-top: 8px;
  color: #6b7280;
}

.no-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}

.no-chart i {
  font-size: 48px;
  margin-bottom: 16px;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-dropdown-link) {
  cursor: pointer;
  color: #409EFF;
}

.chart-view-dialog .el-dialog {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.chart-view-dialog .el-dialog__header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: 0;
  padding: 20px;
}

.chart-view-dialog .el-dialog__header .el-dialog__title {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.chart-view-dialog .el-dialog__headerbtn {
  top: 20px;
  right: 20px;
}

.chart-view-dialog .el-dialog__headerbtn .el-dialog__close {
  color: white;
  font-size: 18px;
}

.chart-view-dialog .el-dialog__headerbtn .el-dialog__close:hover {
  color: #f0f0f0;
}

.chart-view-dialog .el-dialog__body {
  padding: 0;
  background: #f8fafc;
}

.multi-field-selector {
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  padding: 12px;
  background: #fafafa;
}

.field-list {
  margin-bottom: 8px;
}

.field-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.field-item:last-child {
  margin-bottom: 0;
}

.line-style-config {
  margin-top: 16px;
  border: 1px solid #e1e5e9;
  border-radius: 4px;
}

.line-style-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 8px;
}

.line-style-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.line-style-item h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

:deep(.el-collapse-item__header) {
  font-weight: 600;
  background: #f8f9fa;
}

:deep(.el-collapse-item__content) {
  padding: 0;
}

.mini-map {
  background: linear-gradient(135deg, #5470c6, #73c0de);
}

/* 地图配置样式 */
.map-config {
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  padding: 16px;
  background: #fafafa;
  margin-top: 16px;
}

.map-style-config {
  margin-top: 16px;
}

/* 旋转动画 */
@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-view-dialog {
    width: 98% !important;
    top: 1vh !important;
  }

  .chart-view-header {
    padding: 16px;
  }

  .chart-view-header h2 {
    font-size: 20px;
  }

  .chart-view-header .chart-meta {
    gap: 8px;
  }

  .chart-view-header .chart-meta .el-tag {
    font-size: 12px;
  }

  .chart-content {
    padding: 12px;
  }
}
</style>
