<!--Copyright (c) 2025 YycKop-->
<!--MIT License-->
<!--Integrated-Data-Platform-frontend/src/pages/Processing.vue-->
<template>
  <div class="processing-page">
    <div class="page-header">
      <h2>数据处理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showPipelineDialog = true">
          <el-icon>
            <Plus/>
          </el-icon>
          新建处理流程
        </el-button>
      </div>
    </div>

    <el-card>
      <template #header>
        <span>处理流程</span>
      </template>
      <el-table :data="pipelines" v-loading="pipelinesLoading">
        <el-table-column prop="name" label="流程名称"/>
        <el-table-column prop="input_dataset_name" label="输入数据集"/>
        <el-table-column prop="output_dataset_name_display" label="输出数据集"/>
        <el-table-column label="模块数量">
          <template #default="{ row }">
            <el-tag>{{ row.modules?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewPipeline(row)">查看</el-button>
            <el-button size="small" type="success" @click="executePipeline(row)">
              执行
            </el-button>
            <el-button size="small" type="danger" @click="deletePipeline(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 处理流程对话框 -->
    <el-dialog
      v-model="showPipelineDialog"
      :title="editingPipeline ? '编辑处理流程' : '新建处理流程'"
      width="900px"
      @close="handlePipelineClose"
    >
      <el-form
        :model="pipelineForm"
        :rules="pipelineRules"
        ref="pipelineFormRef"
        label-width="120px"
      >
        <el-form-item label="流程名称" prop="name">
          <el-input v-model="pipelineForm.name"/>
        </el-form-item>

        <el-form-item label="输入数据集" prop="input_dataset">
          <el-select
            v-model="pipelineForm.input_dataset"
            placeholder="请选择输入数据集"
            @change="handleInputDatasetChange"
          >
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="输出数据集" prop="output_option">
          <el-radio-group v-model="pipelineForm.output_option">
            <el-radio label="new">创建新数据集</el-radio>
            <el-radio label="existing">选择现有数据集</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="pipelineForm.output_option === 'new'"
          label="数据集类型"
          prop="output_data_type"
        >
          <el-radio-group v-model="pipelineForm.output_data_type">
            <el-radio label="json">JSON</el-radio>
            <el-radio label="csv">CSV</el-radio>
            <el-radio label="excel">Excel</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="pipelineForm.output_option === 'new'"
          label="新数据集名称"
          prop="output_dataset_name"
        >
          <el-input
            v-model="pipelineForm.output_dataset_name"
            placeholder="请输入输出数据集名称"
          />
        </el-form-item>

        <el-form-item
          v-if="pipelineForm.output_option === 'existing'"
          label="选择数据集"
          prop="output_dataset"
        >
          <el-select v-model="pipelineForm.output_dataset" placeholder="请选择输出数据集">
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="pipelineForm.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>

        <el-form-item label="处理模块">
          <div class="pipeline-modules">
            <div
              v-for="(module, index) in pipelineModules"
              :key="index"
              class="module-item"
            >
              <div class="module-header">
                <span class="module-order">步骤 {{ index + 1 }}</span>
                <el-button
                  type="danger"
                  size="small"
                  @click="removePipelineModule(index)"
                >
                  删除
                </el-button>
              </div>

              <el-form :model="module" label-width="80px" class="module-form">
                <el-form-item label="模块名称" prop="name"
                              :rules="[{ required: true, message: '请输入模块名称' }]">
                  <el-input v-model="module.name" placeholder="输入模块名称"/>
                </el-form-item>

                <el-form-item label="模块类型" prop="type"
                              :rules="[{ required: true, message: '请选择模块类型' }]">
                  <el-select v-model="module.type" placeholder="选择模块类型"
                             @change="handleModuleTypeChange(index)">
                    <el-option label="数据过滤" value="filter"/>
                    <el-option label="数据转换" value="transform"/>
                    <el-option label="数据聚合" value="aggregate"/>
                    <el-option label="数据清洗" value="clean"/>
                    <el-option label="数据截取" value="select"/>
                    <!-- 添加数据排序选项 -->
                    <el-option label="数据排序" value="sort"/>
                  </el-select>
                </el-form-item>
              </el-form>

              <!-- 可视化配置区域 -->
              <div v-if="module.type" class="module-config">
                <!-- 过滤模块配置 -->
                <div v-if="module.type === 'filter'" class="config-section">
                  <el-form label-width="80px">
                    <el-form-item label="字段">
                      <el-select v-model="module.configuration.field" placeholder="选择字段">
                        <el-option
                          v-for="column in availableColumns"
                          :key="column"
                          :label="column"
                          :value="column"
                        />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="操作符">
                      <el-select v-model="module.configuration.operator" placeholder="选择操作符">
                        <el-option label="等于 ==" value="=="/>
                        <el-option label="不等于 !=" value="!="/>
                        <el-option label="大于 >" value=">"/>
                        <el-option label="大于等于 >=" value=">="/>
                        <el-option label="小于 <" value="<"/>
                        <el-option label="小于等于 <=" value="<="/>
                        <el-option label="包含 contains" value="contains"/>
                        <el-option label="不包含 not_contains" value="not_contains"/>
                        <el-option label="在列表中 in" value="in"/>
                        <el-option label="不在列表中 not_in" value="not_in"/>
                        <el-option label="为空 is_null" value="is_null"/>
                        <el-option label="不为空 not_null" value="not_null"/>
                      </el-select>
                    </el-form-item>
                    <el-form-item
                      v-if="!['is_null', 'not_null'].includes(module.configuration.operator)"
                      label="值">
                      <el-input
                        v-model="module.configuration.value"
                        placeholder="输入过滤值"
                      />
                    </el-form-item>
                  </el-form>
                </div>

                <!-- 排序模块配置 -->
                <div v-if="module.type === 'sort'" class="config-section">
                  <el-form label-width="80px">
                    <el-form-item label="排序配置">
                      <div class="sort-configs">
                        <div
                          v-for="(sortConfig, sortIndex) in module.configuration.sort_fields"
                          :key="sortIndex"
                          class="sort-item"
                        >
                          <div class="sort-header">
                            <span>排序条件 {{ sortIndex + 1 }}</span>
                            <el-button
                              v-if="module.configuration.sort_fields.length > 1"
                              type="danger"
                              size="small"
                              @click="removeSortConfig(index, sortIndex)"
                            >
                              删除
                            </el-button>
                          </div>

                          <div class="sort-fields">
                            <el-form-item label="排序字段">
                              <el-select
                                v-model="sortConfig.field"
                                placeholder="选择排序字段"
                                style="width: 100%"
                              >
                                <el-option
                                  v-for="column in availableColumns"
                                  :key="column"
                                  :label="column"
                                  :value="column"
                                />
                              </el-select>
                            </el-form-item>

                            <el-form-item label="排序方式">
                              <el-radio-group v-model="sortConfig.order">
                                <el-radio label="asc">升序 (A-Z, 小到大)</el-radio>
                                <el-radio label="desc">降序 (Z-A, 大到小)</el-radio>
                              </el-radio-group>
                            </el-form-item>
                          </div>
                        </div>

                        <el-button
                          @click="addSortConfig(index)"
                          type="primary"
                          size="small"
                          class="add-sort-btn"
                        >
                          添加排序条件
                        </el-button>
                      </div>
                    </el-form-item>

                    <!-- 空值处理选项 -->
                    <el-form-item label="空值处理">
                      <el-radio-group v-model="module.configuration.na_position">
                        <el-radio label="first">空值排在前面</el-radio>
                        <el-radio label="last">空值排在后面</el-radio>
                      </el-radio-group>
                    </el-form-item>

                    <!-- 添加截取功能 -->
                    <el-form-item label="数据截取">
                      <div class="limit-config">
                        <el-checkbox v-model="module.configuration.enable_limit"
                                     @change="handleLimitToggle(index)">
                          启用数据截取
                        </el-checkbox>

                        <div v-if="module.configuration.enable_limit" class="limit-options"
                             style="margin-top: 10px;">
                          <el-form-item label="截取方式">
                            <el-radio-group v-model="module.configuration.limit_type">
                              <el-radio label="top">前 N 行</el-radio>
                              <el-radio label="bottom">后 N 行</el-radio>
                              <el-radio label="range">范围截取</el-radio>
                            </el-radio-group>
                          </el-form-item>

                          <div
                            v-if="module.configuration.limit_type === 'top' || module.configuration.limit_type === 'bottom'"
                            class="limit-single">
                            <el-form-item label="行数">
                              <el-input-number
                                v-model="module.configuration.limit_count"
                                :min="1"
                                :max="10000"
                                placeholder="请输入要截取的行数"
                              />
                              <span class="limit-tip">行</span>
                            </el-form-item>
                          </div>

                          <div v-if="module.configuration.limit_type === 'range'"
                               class="limit-range">
                            <el-form-item label="起始行">
                              <el-input-number
                                v-model="module.configuration.start_row"
                                :min="0"
                                :max="10000"
                                placeholder="起始行号"
                              />
                              <span class="limit-tip">(从0开始)</span>
                            </el-form-item>

                            <el-form-item label="结束行">
                              <el-input-number
                                v-model="module.configuration.end_row"
                                :min="1"
                                :max="10000"
                                placeholder="结束行号"
                              />
                              <span class="limit-tip">(包含)</span>
                            </el-form-item>
                          </div>

                          <!-- 显示预计结果 -->
                          <div v-if="module.configuration.enable_limit" class="limit-preview">
                            <el-alert
                              :title="getLimitPreview(module)"
                              type="info"
                              :closable="false"
                              show-icon
                            />
                          </div>
                        </div>
                      </div>
                    </el-form-item>
                  </el-form>
                </div>

                <!-- 数据截取模块配置 -->
                <div v-if="module.type === 'select'" class="config-section">
                  <el-form label-width="80px">
                    <el-form-item label="选择字段">
                      <!-- 快速操作按钮 -->
                      <div class="quick-actions" style="margin-bottom: 10px;">
                        <el-button size="small" @click="selectAllFields(index)">全选</el-button>
                        <el-button size="small" @click="clearAllFields(index)">清空</el-button>
                        <el-button size="small" @click="invertSelection(index)">反选</el-button>
                        <span style="margin-left: 10px; color: #666;">
          已选择: {{ getSelectedCount(module) }} 个字段
        </span>
                      </div>

                      <!-- 始终保持展开的字段列表 -->
                      <div class="fields-checkbox-container">
                        <div class="fields-list">
                          <div
                            v-for="column in selectModuleAvailableColumns"
                            :key="column"
                            class="field-checkbox-item"
                            :class="{ 'selected': isFieldSelected(module, column) }"
                            @click="toggleFieldSelection(column, index)"
                          >
                            <div class="checkbox-wrapper">
                              <input
                                type="checkbox"
                                :checked="isFieldSelected(module, column)"
                                @change="(e) => handleCheckboxChange(e, column, index)"
                                @click.stop
                              />
                              <span class="checkmark"></span>
                            </div>
                            <span class="field-text">{{ column }}</span>
                          </div>
                        </div>
                      </div>
                    </el-form-item>

                    <!-- 显示已选字段 -->
                    <el-form-item
                      v-if="module.configuration.selected_fields && module.configuration.selected_fields.length > 0"
                      label="已选字段"
                    >
                      <div class="selected-fields-display">
                        <el-tag
                          v-for="field in module.configuration.selected_fields"
                          :key="field"
                          closable
                          @close="removeSelectedField(index, field)"
                          style="margin: 2px 4px;"
                        >
                          {{ field }}
                        </el-tag>
                      </div>
                    </el-form-item>

                    <el-form-item label="操作模式">
                      <el-radio-group v-model="module.configuration.mode">
                        <el-radio label="include">包含选中字段</el-radio>
                        <el-radio label="exclude">排除选中字段</el-radio>
                      </el-radio-group>
                    </el-form-item>

                    <el-form-item
                      label="重命名配置"
                      v-if="module.configuration.selected_fields && module.configuration.selected_fields.length > 0"
                    >
                      <div class="rename-configs">
                        <div
                          v-for="(field, fieldIndex) in module.configuration.selected_fields"
                          :key="fieldIndex"
                          class="rename-item"
                        >
                          <span class="field-name">{{ field }}</span>
                          <el-input
                            v-model="module.configuration.rename_mapping[field]"
                            :placeholder="`新字段名（留空保持原字段名）`"
                            size="small"
                            style="width: 200px; margin-left: 10px;"
                          />
                        </div>
                      </div>
                    </el-form-item>
                  </el-form>
                </div>

                <!-- 转换模块配置 -->
                <div v-if="module.type === 'transform'" class="config-section">
                  <el-form label-width="80px">
                    <el-form-item label="选择字段">
                      <el-select
                        v-model="module.configuration.fields"
                        placeholder="选择要转换的字段"
                        multiple
                        style="width: 100%"
                      >
                        <el-option
                          v-for="column in availableColumns"
                          :key="column"
                          :label="column"
                          :value="column"
                        />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="操作">
                      <el-select v-model="module.configuration.operation" placeholder="选择操作">
                        <el-option label="大写 uppercase" value="uppercase"/>
                        <el-option label="小写 lowercase" value="lowercase"/>
                        <el-option label="去除空格 trim" value="trim"/>
                        <el-option label="四舍五入 round" value="round"/>
                        <el-option label="绝对值 abs" value="abs"/>
                        <el-option label="标准化 standardize" value="standardize"/>
                        <el-option label="归一化 normalize" value="normalize"/>
                        <!-- 添加百分比转换选项 -->
                        <el-option label="百分比转小数 percent_to_decimal"
                                   value="percent_to_decimal"/>
                        <el-option label="小数转百分比 decimal_to_percent"
                                   value="decimal_to_percent"/>
                        <!-- 添加时间数据转换选项 -->
                        <el-option label="提取年份 extract_year" value="extract_year"/>
                        <el-option label="提取月份 extract_month" value="extract_month"/>
                        <el-option label="提取日期 extract_day" value="extract_day"/>
                        <el-option label="提取小时 extract_hour" value="extract_hour"/>
                        <el-option label="提取分钟 extract_minute" value="extract_minute"/>
                        <el-option label="提取秒数 extract_second" value="extract_second"/>
                        <el-option label="提取季度 extract_quarter" value="extract_quarter"/>
                        <el-option label="提取星期 extract_weekday" value="extract_weekday"/>
                      </el-select>
                    </el-form-item>

                    <!-- 添加时间格式配置 -->
                    <el-form-item
                      v-if="module.configuration.operation && module.configuration.operation.startsWith('extract_')"
                      label="时间格式"
                    >
                      <el-select v-model="module.configuration.time_format"
                                 placeholder="选择时间格式">
                        <el-option label="YYYYmmdd (如: 20231225)" value="YYYYmmdd"/>
                        <el-option label="YYYY-mm-dd (如: 2023-12-25)" value="YYYY-mm-dd"/>
                        <el-option label="YYYY/mm/dd (如: 2023/12/25)" value="YYYY/mm/dd"/>
                        <el-option label="YYYY年mm月dd日 (如: 2023年12月25日)"
                                   value="YYYY年mm月dd日"/>
                        <el-option label="hhMMss (如: 143045)" value="hhMMss"/>
                        <el-option label="hh:MM:ss (如: 14:30:45)" value="hh:MM:ss"/>
                        <el-option label="hh时MM分ss秒 (如: 14时30分45秒)" value="hh时MM分ss秒"/>
                        <el-option label="YYYYmmdd hhMMss (如: 20231225 143045)"
                                   value="YYYYmmdd hhMMss"/>
                        <el-option label="YYYY-mm-dd hh:MM:ss (如: 2023-12-25 14:30:45)"
                                   value="YYYY-mm-dd hh:MM:ss"/>
                        <el-option label="时间戳 timestamp" value="timestamp"/>
                        <el-option label="自动识别 auto" value="auto"/>
                      </el-select>
                    </el-form-item>
                    <el-form-item
                      v-if="module.configuration.fields && module.configuration.fields.length > 0"
                      label="新字段名前缀"
                    >
                      <el-input
                        v-model="module.configuration.new_field_prefix"
                        placeholder="留空则覆盖原字段"
                      />
                    </el-form-item>
                    <!-- 精度配置 -->
                    <el-form-item
                      v-if="module.configuration.operation && ['percent_to_decimal', 'decimal_to_percent', 'round'].includes(module.configuration.operation)"
                      label="小数位数"
                    >
                      <el-input-number
                        v-model="module.configuration.decimal_places"
                        :min="0"
                        :max="10"
                        placeholder="保留小数位数"
                      />
                    </el-form-item>
                  </el-form>
                </div>

                <!-- 聚合模块配置 - 修改后的多字段版本 -->
                <div v-if="module.type === 'aggregate'" class="config-section">
                  <el-form label-width="80px">
                    <el-form-item label="分组字段">
                      <el-select
                        v-model="module.configuration.group_by"
                        placeholder="选择分组字段"
                        multiple
                        clearable
                        style="width: 100%"
                      >
                        <el-option
                          v-for="column in availableColumns"
                          :key="column"
                          :label="column"
                          :value="column"
                        />
                      </el-select>
                    </el-form-item>

                    <el-form-item label="聚合配置">
                      <div class="aggregation-configs">
                        <div
                          v-for="(aggConfig, aggIndex) in module.configuration.aggregations"
                          :key="aggIndex"
                          class="aggregation-item"
                        >
                          <div class="aggregation-header">
                            <span>聚合配置 {{ aggIndex + 1 }}</span>
                            <el-button
                              v-if="module.configuration.aggregations.length > 1"
                              type="danger"
                              size="small"
                              @click="removeAggregationConfig(index, aggIndex)"
                            >
                              删除
                            </el-button>
                          </div>

                          <div class="aggregation-fields">
                            <el-form-item label="聚合字段">
                              <el-select
                                v-model="aggConfig.field"
                                placeholder="选择聚合字段"
                                style="width: 100%"
                              >
                                <el-option
                                  v-for="column in availableColumns"
                                  :key="column"
                                  :label="column"
                                  :value="column"
                                />
                              </el-select>
                            </el-form-item>

                            <el-form-item label="聚合操作">
                              <el-select
                                v-model="aggConfig.operation"
                                placeholder="选择聚合操作"
                                style="width: 100%"
                              >
                                <el-option label="求和 sum" value="sum"/>
                                <el-option label="平均值 mean" value="mean"/>
                                <el-option label="计数 count" value="count"/>
                                <el-option label="最大值 max" value="max"/>
                                <el-option label="最小值 min" value="min"/>
                                <el-option label="标准差 std" value="std"/>
                                <el-option label="方差 var" value="var"/>
                                <el-option label="中位数 median" value="median"/>
                                <el-option label="第一个值 first" value="first"/>
                                <el-option label="最后一个值 last" value="last"/>
                              </el-select>
                            </el-form-item>

                            <el-form-item label="输出名称">
                              <el-input
                                v-model="aggConfig.output_name"
                                :placeholder="getDefaultOutputName(aggConfig)"
                              />
                            </el-form-item>
                          </div>
                        </div>

                        <el-button
                          @click="addAggregationConfig(index)"
                          type="primary"
                          size="small"
                          class="add-aggregation-btn"
                        >
                          添加聚合配置
                        </el-button>
                      </div>
                    </el-form-item>
                  </el-form>
                </div>

                <!-- 清洗模块配置 -->
                <div v-if="module.type === 'clean'" class="config-section">
                  <el-form label-width="80px">
                    <el-form-item label="字段">
                      <el-select v-model="module.configuration.field" placeholder="选择字段">
                        <el-option
                          v-for="column in availableColumns"
                          :key="column"
                          :label="column"
                          :value="column"
                        />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="操作">
                      <el-select v-model="module.configuration.operation" placeholder="选择操作">
                        <el-option label="填充空值 fill_na" value="fill_na"/>
                        <el-option label="去除重复 remove_duplicates" value="remove_duplicates"/>
                        <el-option label="去除空值 remove_na" value="remove_na"/>
                      </el-select>
                    </el-form-item>
                    <el-form-item v-if="module.configuration.operation === 'fill_na'"
                                  label="填充值">
                      <el-input
                        v-model="module.configuration.value"
                        placeholder="输入填充值"
                      />
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </div>
            <el-button @click="addPipelineModule" class="add-module-btn">
              <el-icon>
                <Plus/>
              </el-icon>
              添加处理模块
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPipelineDialog = false">取消</el-button>
        <el-button type="primary" :loading="pipelineSaving" @click="handlePipelineSave">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog
      v-model="showExecutionResult"
      title="处理流程执行结果"
      width="600px"
    >
      <div v-if="executionResult">
        <el-alert
          :title="`处理完成！共处理 ${executionResult.original_records} 条记录，输出 ${executionResult.processed_records} 条记录`"
          type="success"
          :closable="false"
        />

        <el-divider/>

        <h4>执行日志：</h4>
        <el-table :data="executionResult.execution_log" size="small">
          <el-table-column prop="module" label="模块"/>
          <el-table-column prop="type" label="类型"/>
          <el-table-column prop="before_count" label="处理前"/>
          <el-table-column prop="after_count" label="处理后"/>
          <el-table-column prop="records_affected" label="影响记录">
            <template #default="{ row }">
              <el-tag :type="row.records_affected > 0 ? 'info' : 'success'">
                {{ row.records_affected }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 20px; text-align: center;">
          <el-button
            type="primary"
            @click="showExecutionResult = false"
          >
            确定
          </el-button>
          <el-button
            v-if="executionResult.output_dataset_id"
            @click="viewOutputDataset(executionResult.output_dataset_id)"
          >
            查看输出数据集
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive, computed, onMounted, watch} from 'vue'
import {useRouter} from 'vue-router'
import {processingAPI} from '../api/processing'
import {datasetsAPI} from '../api/datasets'
import {ElMessage, ElMessageBox} from 'element-plus'
import {InfoFilled} from '@element-plus/icons-vue'

const router = useRouter()

const pipelinesLoading = ref(false)
const pipelineSaving = ref(false)
const showPipelineDialog = ref(false)
const showExecutionResult = ref(false)

const pipelines = ref([])
const datasets = ref([])
const datasetColumns = ref([])
const editingPipeline = ref(null)
const executionResult = ref(null)

const pipelineFormRef = ref()

const pipelineForm = reactive({
  name: '',
  input_dataset: '',
  output_option: 'new',
  output_dataset_name: '',
  output_dataset: '',
  output_data_type: 'json', // 修改为 output_data_type
  description: ''
})

const pipelineModules = ref([])

const pipelineRules = {
  name: [
    {required: true, message: '请输入流程名称', trigger: 'blur'}
  ],
  input_dataset: [
    {required: true, message: '请选择输入数据集', trigger: 'change'}
  ],
  output_dataset_name: [
    {required: true, message: '请输入输出数据集名称', trigger: 'blur'}
  ],
  output_dataset: [
    {required: true, message: '请选择输出数据集', trigger: 'change'}
  ],
  output_data_type: [  // 修改为 output_data_type
    {required: true, message: '请选择数据类型', trigger: 'change'}
  ]
}


// 计算属性：动态生成当前可用的字段列表
const availableColumns = computed(() => {
  let columns = [...datasetColumns.value];

  // 只处理当前模块之前的模块，不影响当前模块自身
  for (let i = 0; i < pipelineModules.value.length; i++) {
    const module = pipelineModules.value[i];

    // 跳过当前正在配置的模块
    // 这里我们只处理 transform 和 aggregate 模块，因为它们会生成新字段
    // 不处理 select 模块，因为它只是选择字段，不应该影响后续模块的可用字段列表

    if (module.type === 'transform') {
      const config = module.configuration;
      const originalField = config.field;
      const newField = config.new_field || originalField;
      const operation = config.operation;

      // 如果转换操作生成了新字段，且不是覆盖原字段
      if (newField && newField !== originalField && operation) {
        if (!columns.includes(newField)) {
          columns.push(newField);
        }
      }
    } else if (module.type === 'aggregate') {
      // 聚合模块会生成全新的字段结构
      const config = module.configuration;
      const groupBy = config.group_by || [];
      const aggregations = config.aggregations || [];

      const aggregationColumns = [...groupBy];
      aggregations.forEach(agg => {
        if (agg.output_name) {
          aggregationColumns.push(agg.output_name);
        } else if (agg.field && agg.operation) {
          const operationNames = {
            sum: '总和',
            mean: '平均值',
            count: '计数',
            max: '最大值',
            min: '最小值',
            std: '标准差',
            var: '方差',
            median: '中位数',
            first: '第一个值',
            last: '最后一个值'
          };
          const outputName = `${agg.field}_${operationNames[agg.operation] || agg.operation}`;
          aggregationColumns.push(outputName);
        }
      });

      columns = [...aggregationColumns];
    }
    // 注意：我们移除了对 select 模块的处理，因为它不应该影响可用字段列表
  }

  return columns;
});

// 为数据截取模块单独创建一个计算属性，只包含原始字段
const selectModuleAvailableColumns = computed(() => {
  return [...datasetColumns.value];
});

watch(() => pipelineForm.input_dataset, async (newDatasetId) => {
  if (newDatasetId) {
    await loadDatasetColumnsByDatasetId(newDatasetId)
  } else {
    datasetColumns.value = []
  }
})

// 处理输入数据集变化（用于 select 的 change 事件）
const handleInputDatasetChange = async (datasetId) => {
  if (datasetId) {
    await loadDatasetColumnsByDatasetId(datasetId)

    // 重置输出数据集相关字段
    pipelineForm.output_dataset_name = ''
    pipelineForm.output_dataset = ''
  } else {
    datasetColumns.value = []
  }
}

// 监听数据截取模块的字段选择变化，初始化重命名映射
watch(() => pipelineModules.value, (newModules) => {
  newModules.forEach((module, index) => {
    if (module.type === 'select' && module.configuration.selected_fields) {
      // 确保重命名映射对象存在
      if (!module.configuration.rename_mapping) {
        module.configuration.rename_mapping = {}
      }

      // 为新增的字段初始化重命名映射
      module.configuration.selected_fields.forEach(field => {
        if (!module.configuration.rename_mapping[field]) {
          module.configuration.rename_mapping[field] = ''
        }
      })

      // 清理已删除字段的重命名映射
      Object.keys(module.configuration.rename_mapping).forEach(key => {
        if (!module.configuration.selected_fields.includes(key)) {
          delete module.configuration.rename_mapping[key]
        }
      })
    }
  })
}, {deep: true})

// 检查字段是否已选择
const isFieldSelected = (module, field) => {
  return module.configuration.selected_fields?.includes(field) || false
}

// 切换字段选择
const toggleField = (field, moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]
  if (!module.configuration.selected_fields) {
    module.configuration.selected_fields = []
  }

  const isSelected = module.configuration.selected_fields.includes(field)
  if (isSelected) {
    // 取消选择
    const fieldIndex = module.configuration.selected_fields.indexOf(field)
    module.configuration.selected_fields.splice(fieldIndex, 1)
  } else {
    // 选择
    module.configuration.selected_fields.push(field)
  }

  handleSelectFieldsChange(moduleIndex)
}
const toggleFieldSelection = (field, moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]

  // 确保selected_fields存在且是数组
  if (!module.configuration.selected_fields || !Array.isArray(module.configuration.selected_fields)) {
    module.configuration.selected_fields = []
  }

  const currentSelected = module.configuration.selected_fields
  const fieldIndex = currentSelected.indexOf(field)

  if (fieldIndex > -1) {
    // 如果已选中，移除
    currentSelected.splice(fieldIndex, 1)
  } else {
    // 如果未选中，添加
    currentSelected.push(field)
  }

  // 触发更新
  handleSelectFieldsChange(moduleIndex)
}

// 处理复选框变化
const handleCheckboxChange = (event, field, moduleIndex) => {
  const checked = event.target.checked
  const module = pipelineModules.value[moduleIndex]

  // 确保selected_fields存在且是数组
  if (!module.configuration.selected_fields || !Array.isArray(module.configuration.selected_fields)) {
    module.configuration.selected_fields = []
  }

  const currentSelected = module.configuration.selected_fields

  if (checked) {
    // 如果选中且不在数组中，添加
    if (!currentSelected.includes(field)) {
      currentSelected.push(field)
    }
  } else {
    // 如果取消选中且在数组中，移除
    const fieldIndex = currentSelected.indexOf(field)
    if (fieldIndex > -1) {
      currentSelected.splice(fieldIndex, 1)
    }
  }

  // 触发更新
  handleSelectFieldsChange(moduleIndex)
}
// 处理原生checkbox变化
const handleFieldChange = (event, field, moduleIndex) => {
  const checked = event.target.checked
  const module = pipelineModules.value[moduleIndex]
  if (!module.configuration.selected_fields) {
    module.configuration.selected_fields = []
  }

  if (checked) {
    // 添加字段
    if (!module.configuration.selected_fields.includes(field)) {
      module.configuration.selected_fields.push(field)
    }
  } else {
    // 移除字段
    const fieldIndex = module.configuration.selected_fields.indexOf(field)
    if (fieldIndex > -1) {
      module.configuration.selected_fields.splice(fieldIndex, 1)
    }
  }

  handleSelectFieldsChange(moduleIndex)
}

// 处理字段选择变化
const handleSelectFieldsChange = (moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]
  const config = module.configuration

  // 确保重命名映射对象存在
  if (!config.rename_mapping) {
    config.rename_mapping = {}
  }

  // 为新增的字段初始化重命名映射
  if (config.selected_fields) {
    config.selected_fields.forEach(field => {
      if (!config.rename_mapping[field]) {
        config.rename_mapping[field] = ''
      }
    })

    // 清理已删除字段的重命名映射
    Object.keys(config.rename_mapping).forEach(key => {
      if (!config.selected_fields.includes(key)) {
        delete config.rename_mapping[key]
      }
    })
  }
}

// 移除已选字段
const removeSelectedField = (moduleIndex, fieldToRemove) => {
  const module = pipelineModules.value[moduleIndex]
  const config = module.configuration

  // 从选中字段列表中移除
  config.selected_fields = config.selected_fields.filter(field => field !== fieldToRemove)

  // 从重命名映射中移除
  if (config.rename_mapping && config.rename_mapping[fieldToRemove]) {
    delete config.rename_mapping[fieldToRemove]
  }
}

// 全选字段
const selectAllFields = (moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]
  module.configuration.selected_fields = [...selectModuleAvailableColumns.value]
  handleSelectFieldsChange(moduleIndex)
}
// 清空字段选择
const clearAllFields = (moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]
  module.configuration.selected_fields = []
  module.configuration.rename_mapping = {}
}

// 反选
const invertSelection = (moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]
  const currentSelected = module.configuration.selected_fields || []
  const invertedSelection = selectModuleAvailableColumns.value.filter(
    column => !currentSelected.includes(column)
  )
  module.configuration.selected_fields = invertedSelection
  handleSelectFieldsChange(moduleIndex)
}

// 获取已选数量
const getSelectedCount = (module) => {
  return module.configuration.selected_fields?.length || 0
}

const getModuleTypeTag = (type) => {
  const typeMap = {
    filter: 'success',
    transform: 'warning',
    aggregate: 'primary',
    clean: 'info',
    select: 'info'
  }
  return typeMap[type] || 'info'
}

const getModuleTypeText = (type) => {
  // 先映射到前端类型
  const frontendType = reverseModuleTypeMapping[type] || type
  const typeMap = {
    filter: '数据过滤',
    transform: '数据转换',
    aggregate: '数据聚合',
    clean: '数据清洗',
    select: '数据截取'
  }
  return typeMap[frontendType] || type
}
const loadPipelines = async () => {
  pipelinesLoading.value = true
  try {
    pipelines.value = await processingAPI.getPipelines()
  } catch (error) {
    ElMessage.error('加载处理流程失败')
  } finally {
    pipelinesLoading.value = false
  }
}

const loadDatasets = async () => {
  try {
    datasets.value = await datasetsAPI.getDatasets()
  } catch (error) {
    ElMessage.error('加载数据集失败')
  }
}

// 为现有流程加载列名
const loadDatasetColumns = async (pipelineId) => {
  try {
    const response = await processingAPI.getDatasetColumns(pipelineId)
    datasetColumns.value = response.columns || []
  } catch (error) {
    console.error('加载列名失败:', error)
    datasetColumns.value = []
  }
}

// 为新建流程加载列名
const loadDatasetColumnsByDatasetId = async (datasetId) => {
  try {
    const response = await processingAPI.getDatasetColumnsById(datasetId)
    datasetColumns.value = response.columns || []
  } catch (error) {
    console.error('根据数据集ID加载列名失败:', error)
    datasetColumns.value = []
  }
}

const handleModuleTypeChange = (index) => {
  const module = pipelineModules.value[index]

  // 保存当前配置中的有效字段（如已选择的字段）
  const currentConfig = module.configuration || {}
  const preservedFields = {}

  // 对于select模块，保留已选择的字段
  if (module.type === 'select' && currentConfig.selected_fields) {
    preservedFields.selected_fields = currentConfig.selected_fields
    preservedFields.rename_mapping = currentConfig.rename_mapping || {}
  }

  // 获取新的默认配置
  const defaultConfig = getDefaultConfig(module.type)

  // 合并配置，保留需要保留的字段
  module.configuration = {
    ...defaultConfig,
    ...preservedFields
  }
}

const getDefaultConfig = (type) => {
  const defaults = {
    filter: {
      field: '',
      operator: '',
      value: ''
    },
    transform: {
      fields: [],
      operation: '',
      new_field_prefix: '',
      time_format: 'auto',
      decimal_places: 2
    },
    aggregate: {
      group_by: [],
      aggregations: [
        {
          field: '',
          operation: '',
          output_name: ''
        }
      ]
    },
    clean: {
      field: '',
      operation: '',
      value: ''
    },
    select: {
      selected_fields: [],
      mode: 'include',
      rename_mapping: {}
    },
    // 更新排序模块默认配置
    sort: {
      sort_fields: [
        {
          field: '',
          order: 'asc'
        }
      ],
      na_position: 'last',
      // 添加截取功能配置
      enable_limit: false,
      limit_type: 'top', // top, bottom, range
      limit_count: 10,
      start_row: 0,
      end_row: 10
    }
  }
  return JSON.parse(JSON.stringify(defaults[type]))
}
// 添加排序配置
const addSortConfig = (moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]
  if (!module.configuration.sort_fields) {
    module.configuration.sort_fields = []
  }
  module.configuration.sort_fields.push({
    field: '',
    order: 'asc'
  })
}

// 删除排序配置
const removeSortConfig = (moduleIndex, sortIndex) => {
  const module = pipelineModules.value[moduleIndex]
  if (module.configuration.sort_fields.length > 1) {
    module.configuration.sort_fields.splice(sortIndex, 1)
  }
}
const getLimitPreview = (module) => {
  const config = module.configuration
  if (!config.enable_limit) return '未启用数据截取'

  switch (config.limit_type) {
    case 'top':
      return `将截取排序后的前 ${config.limit_count} 行数据`
    case 'bottom':
      return `将截取排序后的后 ${config.limit_count} 行数据`
    case 'range':
      return `将截取排序后的第 ${config.start_row} 行到第 ${config.end_row} 行数据（共 ${config.end_row - config.start_row + 1} 行）`
    default:
      return '未知的截取方式'
  }
}

// 添加聚合配置的方法
const addAggregationConfig = (moduleIndex) => {
  const module = pipelineModules.value[moduleIndex]
  if (!module.configuration.aggregations) {
    module.configuration.aggregations = []
  }
  module.configuration.aggregations.push({
    field: '',
    operation: '',
    output_name: ''
  })
}


const removeAggregationConfig = (moduleIndex, aggIndex) => {
  const module = pipelineModules.value[moduleIndex]
  if (module.configuration.aggregations.length > 1) {
    module.configuration.aggregations.splice(aggIndex, 1)
  }
}

const getDefaultOutputName = (aggConfig) => {
  if (aggConfig.field && aggConfig.operation) {
    const operationNames = {
      sum: '总和',
      mean: '平均值',
      count: '计数',
      max: '最大值',
      min: '最小值',
      std: '标准差',
      var: '方差',
      median: '中位数',
      first: '第一个值',
      last: '最后一个值'
    }
    return `${aggConfig.field}_${operationNames[aggConfig.operation] || aggConfig.operation}`
  }
  return '自动生成列名'
}
const moduleTypeMapping = {
  'filter': 'data_filter',
  'transform': 'data_transform',
  'aggregate': 'data_aggregate',
  'clean': 'data_clean',
  'select': 'data_select',
  'sort': 'data_sort'  // 添加排序模块映射
}

// 同时添加反向映射，用于显示
const reverseModuleTypeMapping = {
  'data_filter': 'filter',
  'data_transform': 'transform',
  'data_aggregate': 'aggregate',
  'data_clean': 'clean',
  'data_select': 'select',
  'data_sort': 'sort'  // 添加排序模块反向映射
}

const handlePipelineSave = async () => {
  if (!pipelineFormRef.value) return

  await pipelineFormRef.value.validate(async (valid) => {
    if (valid) {
      // 验证模块
      for (let i = 0; i < pipelineModules.value.length; i++) {
        const module = pipelineModules.value[i]
        if (!module.name || !module.type) {
          ElMessage.error(`请完善第 ${i + 1} 个模块的配置`)
          return
        }
      }

      pipelineSaving.value = true
      try {
        // 构建基本数据
        const pipelineData = {
          name: pipelineForm.name,
          input_dataset: pipelineForm.input_dataset,
          description: pipelineForm.description,
          output_data_type: pipelineForm.output_data_type,
        }

        // 处理输出数据集选项
        if (pipelineForm.output_option === 'new') {
          pipelineData.output_dataset_name = pipelineForm.output_dataset_name
          pipelineData.output_dataset = null
        } else {
          pipelineData.output_dataset = pipelineForm.output_dataset
          pipelineData.output_dataset_name = ''
        }

        // 构建模块数据 - 简化格式
        pipelineData.modules = pipelineModules.value.map((module, index) => {
          const baseModule = {
            name: module.name || `模块 ${index + 1}`,
            type: module.type,
            order: index + 1,
          }

          // 确保配置字段存在且是对象
          let configuration = {}
          if (module.configuration && typeof module.configuration === 'object') {
            configuration = {...module.configuration}
          }

          // 根据模块类型清理配置
          switch (module.type) {
            case 'filter':
              configuration = {
                field: configuration.field || '',
                operator: configuration.operator || '',
                value: configuration.value || ''
              }
              break
            case 'transform':
              configuration = {
                fields: Array.isArray(configuration.fields) ? configuration.fields : [],
                operation: configuration.operation || '',
                new_field_prefix: configuration.new_field_prefix || '',
                time_format: configuration.time_format || 'auto',
                decimal_places: configuration.decimal_places || 2
              }
              break
            case 'aggregate':
              configuration = {
                group_by: Array.isArray(configuration.group_by) ? configuration.group_by : [],
                aggregations: (Array.isArray(configuration.aggregations) ? configuration.aggregations : []).map(agg => ({
                  field: agg.field || '',
                  operation: agg.operation || '',
                  output_name: agg.output_name || ''
                }))
              }
              break
            case 'clean':
              configuration = {
                field: configuration.field || '',
                operation: configuration.operation || '',
                value: configuration.value || ''
              }
              break
            case 'select':
              configuration = {
                selected_fields: Array.isArray(configuration.selected_fields) ? configuration.selected_fields : [],
                mode: configuration.mode || 'include',
                rename_mapping: configuration.rename_mapping || {}
              }
              break
            case 'sort':
              configuration = {
                sort_fields: (Array.isArray(configuration.sort_fields) ? configuration.sort_fields : []).map(sort => ({
                  field: sort.field || '',
                  order: sort.order || 'asc'
                })),
                na_position: configuration.na_position || 'last',
                enable_limit: Boolean(configuration.enable_limit),
                limit_type: configuration.limit_type || 'top',
                limit_count: configuration.limit_count || 10,
                start_row: configuration.start_row || 0,
                end_row: configuration.end_row || 10
              }
              break
          }

          return {
            ...baseModule,
            configuration: configuration
          }
        })

        console.log('🚀 发送的完整数据:', JSON.stringify(pipelineData, null, 2))

        if (editingPipeline.value) {
          await processingAPI.updatePipeline(editingPipeline.value.id, pipelineData)
          ElMessage.success('更新成功')
        } else {
          await processingAPI.createPipeline(pipelineData)
          ElMessage.success('创建成功')
        }
        showPipelineDialog.value = false
        loadPipelines()
      } catch (error) {
        console.error('💥 保存失败详情:', error)
        console.error('🔍 错误响应数据:', error.response?.data)

        // 改进的错误显示
        if (error.response?.data?.modules) {
          // 显示每个模块的具体错误
          error.response.data.modules.forEach((moduleErrors, index) => {
            if (moduleErrors && typeof moduleErrors === 'object') {
              Object.keys(moduleErrors).forEach(field => {
                const errors = moduleErrors[field]
                if (Array.isArray(errors)) {
                  ElMessage.error(`模块 ${index + 1} - ${field}: ${errors.join(', ')}`)
                }
              })
            }
          })
        } else if (error.response?.data) {
          // 显示其他错误
          for (const field in error.response.data) {
            const errors = error.response.data[field]
            if (Array.isArray(errors)) {
              ElMessage.error(`${field}: ${errors.join(', ')}`)
            } else if (typeof errors === 'string') {
              ElMessage.error(`${field}: ${errors}`)
            }
          }
        } else {
          ElMessage.error('保存失败: ' + (error.message || '未知错误'))
        }
      } finally {
        pipelineSaving.value = false
      }
    }
  })
}
// 添加数据验证函数
const validatePipelineData = (data) => {
  // 检查必填字段
  if (!data.name || data.name.trim() === '') {
    return {valid: false, error: '流程名称不能为空'}
  }

  if (!data.input_dataset) {
    return {valid: false, error: '输入数据集不能为空'}
  }

  if (!data.modules || data.modules.length === 0) {
    return {valid: false, error: '至少需要一个处理模块'}
  }

  // 检查每个模块
  for (let i = 0; i < data.modules.length; i++) {
    const module = data.modules[i]

    if (!module.name || module.name.trim() === '') {
      return {valid: false, error: `第 ${i + 1} 个模块名称不能为空`}
    }

    if (!module.type) {
      return {valid: false, error: `第 ${i + 1} 个模块类型不能为空`}
    }

    // 检查配置字段
    if (!module.configuration) {
      return {valid: false, error: `第 ${i + 1} 个模块配置不能为空`}
    }

    // 根据模块类型检查特定字段
    if (module.type === 'select') {
      const config = module.configuration
      if (!config.selected_fields || !Array.isArray(config.selected_fields) || config.selected_fields.length === 0) {
        return {valid: false, error: `第 ${i + 1} 个数据截取模块必须选择字段`}
      }
    }
  }

  return {valid: true}
}
const handlePipelineClose = () => {
  pipelineFormRef.value?.resetFields()
  Object.assign(pipelineForm, {
    name: '',
    input_dataset: '',
    output_option: 'new',
    output_dataset_name: '',
    output_dataset: '',
    description: ''
  })
  pipelineModules.value = []
  datasetColumns.value = []
  editingPipeline.value = null
}

const addPipelineModule = () => {
  pipelineModules.value.push({
    name: `处理模块 ${pipelineModules.value.length + 1}`,
    type: '',
    configuration: {}
  })
}

const removePipelineModule = (index) => {
  pipelineModules.value.splice(index, 1)
}

const viewPipeline = async (pipeline) => {
  editingPipeline.value = pipeline
  Object.assign(pipelineForm, {
    name: pipeline.name,
    input_dataset: pipeline.input_dataset,
    output_option: pipeline.output_dataset ? 'existing' : 'new',
    output_dataset_name: pipeline.output_dataset_name || '',
    output_dataset: pipeline.output_dataset || '',
    output_data_type: pipeline.output_data_type || 'json', // 设置数据集类型
    description: pipeline.description
  })

  // 加载数据集列名
  if (pipeline.input_dataset) {
    await loadDatasetColumns(pipeline.id)
  }

  // 处理模块数据 - 使用反向映射将后端类型转换为前端类型
  pipelineModules.value = pipeline.modules?.map(module => {
    const config = {...module.configuration}

    // 将后端类型映射回前端类型用于显示
    const frontendType = reverseModuleTypeMapping[module.type] || module.type

    // 如果是聚合模块且是旧版本配置，转换为新格式
    if (frontendType === 'aggregate' && config.group_by && typeof config.group_by === 'string') {
      config.group_by = [config.group_by]
      if (config.aggregate_field && config.operation) {
        config.aggregations = [{
          field: config.aggregate_field,
          operation: config.operation,
          output_name: config.output_name || `${config.aggregate_field}_${config.operation}`
        }]
      } else {
        config.aggregations = [{field: '', operation: '', output_name: ''}]
      }
      // 删除旧字段
      delete config.aggregate_field
      delete config.operation
      delete config.output_name
    }

    return {
      name: module.name,
      type: frontendType, // 使用前端类型用于显示
      configuration: config
    }
  }) || []

  showPipelineDialog.value = true
}

const executePipeline = async (pipeline) => {
  try {
    await ElMessageBox.confirm(
      `确定要执行处理流程 "${pipeline.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const result = await processingAPI.executePipeline(pipeline.id)
    executionResult.value = result
    showExecutionResult.value = true
    ElMessage.success(`执行成功，处理了 ${result.processed_records} 条记录`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败: ' + (error.response?.data?.error || error.message))
    }
  }
}

const viewOutputDataset = (datasetId) => {
  router.push('/datasets')
  showExecutionResult.value = false
}

const deletePipeline = async (pipeline) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除处理流程 "${pipeline.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await processingAPI.deletePipeline(pipeline.id)
    ElMessage.success('删除成功')
    loadPipelines()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadPipelines()
  loadDatasets()
})
</script>

<style scoped>
.processing-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pipeline-modules {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  max-height: 500px;
  overflow-y: auto;
}

.module-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e6e6e6;
}

.module-order {
  font-weight: bold;
  color: #409EFF;
}

.module-form {
  margin-bottom: 15px;
}

.module-config {
  margin-top: 10px;
}

.config-section {
  background: white;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}

.add-module-btn {
  width: 100%;
  margin-top: 10px;
}

/* 聚合配置样式 */
.aggregation-configs {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fafafa;
}

.aggregation-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}

.aggregation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e6e6e6;
  font-weight: bold;
  color: #409EFF;
}

.aggregation-fields {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  align-items: start;
}

.add-aggregation-btn {
  width: 100%;
  margin-top: 10px;
}

.rename-configs {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fafafa;
  max-height: 200px;
  overflow-y: auto;
}

.rename-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}

.rename-item:last-child {
  margin-bottom: 0;
}

.field-name {
  font-weight: bold;
  color: #409EFF;
  min-width: 120px;
}

/* 字段选择容器 */
.fields-container {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fafafa;
  max-height: 300px;
  overflow-y: auto;
}

.field-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin: 4px 0;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.field-item:hover {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.field-item.selected {
  border-color: #409EFF;
  background-color: #ecf5ff;
}

.field-checkbox {
  margin-right: 8px;
}

.field-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.field-label {
  flex: 1;
  user-select: none;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.fields-checkbox-container {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  background-color: #fafafa;
  max-height: 300px;
  overflow-y: auto;
}

.fields-list {
  padding: 10px;
}

.field-checkbox-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin: 4px 0;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.field-checkbox-item:hover {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.field-checkbox-item.selected {
  border-color: #409EFF;
  background-color: #ecf5ff;
}

.checkbox-wrapper {
  position: relative;
  margin-right: 10px;
}

.checkbox-wrapper input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.checkmark {
  position: relative;
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 2px;
  transition: all 0.2s ease;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark {
  background-color: #409EFF;
  border-color: #409EFF;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.field-text {
  flex: 1;
  user-select: none;
  font-size: 14px;
}

.selected-fields-display {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background-color: #f9f9f9;
  min-height: 40px;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.fields-checkbox-container {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  background-color: #fafafa;
  max-height: 300px;
  overflow-y: auto;
}

.fields-list {
  padding: 10px;
}

.field-checkbox-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin: 4px 0;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.field-checkbox-item:hover {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.field-checkbox-item.selected {
  border-color: #409EFF;
  background-color: #ecf5ff;
}

.checkbox-wrapper {
  position: relative;
  margin-right: 10px;
}

.checkbox-wrapper input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.checkmark {
  position: relative;
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 2px;
  transition: all 0.2s ease;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark {
  background-color: #409EFF;
  border-color: #409EFF;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.field-text {
  flex: 1;
  user-select: none;
  font-size: 14px;
}

.selected-fields-display {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background-color: #f9f9f9;
  min-height: 40px;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.sort-configs {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 10px;
  background-color: #fafafa;
}

.sort-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}

.sort-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e6e6e6;
  font-weight: bold;
  color: #409EFF;
}

.sort-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  align-items: start;
}

.add-sort-btn {
  width: 100%;
  margin-top: 10px;
}

.limit-config {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 15px;
  background-color: #f9f9f9;
}

.limit-options {
  margin-left: 20px;
  border-left: 2px solid #409EFF;
  padding-left: 15px;
}

.limit-single,
.limit-range {
  margin: 10px 0;
}

.limit-tip {
  margin-left: 8px;
  color: #666;
  font-size: 12px;
}

.limit-preview {
  margin-top: 10px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .aggregation-fields {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .aggregation-fields {
    grid-template-columns: 1fr;
  }

  .rename-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .field-name {
    margin-bottom: 5px;
  }

  .rename-item .el-input {
    width: 100% !important;
    margin-left: 0 !important;
  }

  .field-checkbox-item {
    padding: 6px 8px;
  }

  .quick-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .quick-actions .el-button {
    width: 100%;
    margin-bottom: 5px;
  }

  .sort-fields {
    grid-template-columns: 1fr;
  }

  .limit-options {
    margin-left: 10px;
    padding-left: 10px;
  }

  .limit-range .el-form-item {
    margin-bottom: 8px;
  }
}
</style>
