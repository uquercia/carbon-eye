<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  Activity,
  Database,
  FileImage,
  Image,
  PlugZap,
  Upload,
  Waves,
} from 'lucide-vue-next'
import { ElProgress, ElTable, ElTableColumn, ElTag } from 'element-plus'
import AppChart from '../../shared/components/AppChart.vue'
import BuildingMap from './components/BuildingMap.vue'
import MetricTile from './components/MetricTile.vue'
import { fetchDashboard, fetchUploadTask, uploadCampusImage } from './api/dashboardApi'
import type { DashboardApiResponse, UploadTaskResponse } from './api/dashboardApi'
import {
  behaviorImpacts as fallbackBehaviorImpacts,
  behaviorScores as fallbackBehaviorScores,
  buildingRecords as fallbackBuildingRecords,
  recognitionSamples as fallbackRecognitionSamples,
  trainingImages as fallbackTrainingImages,
  trendData as fallbackTrendData,
} from './data/campusData'
import type {
  BehaviorImpact,
  BehaviorScore,
  BuildingRecord,
  RecognitionSample,
  TrainingImage,
  TrendPoint,
} from './data/campusData'
import type { ChartOption } from './types/echarts'

const loadingText = ref('正在连接后端 API')
const apiError = ref('')
const uploadInputRef = ref<HTMLInputElement>()
const uploadStatus = ref('等待上传校园图片')
const uploadedImage = ref<UploadTaskResponse | null>(null)
const uploading = ref(false)
const analyzing = ref(false)
const uploadPercent = ref(0)
const analysisPercent = ref(0)
let pollingTimer: number | null = null

const buildingRecords = ref<BuildingRecord[]>(fallbackBuildingRecords)
const behaviorScores = ref<BehaviorScore[]>(fallbackBehaviorScores)
const trendData = ref<TrendPoint[]>(fallbackTrendData)
const recognitionSamples = ref<RecognitionSample[]>(fallbackRecognitionSamples)
const behaviorImpacts = ref<BehaviorImpact[]>(fallbackBehaviorImpacts)
const trainingImages = ref<TrainingImage[]>(fallbackTrainingImages)

function applyDashboardData(data: DashboardApiResponse) {
  buildingRecords.value = data.buildings.map((item) => ({
    id: item.id,
    name: item.name,
    zone: item.zone,
    major: item.major,
    electricityActual: item.electricity_actual,
    electricityPredicted: item.electricity_predicted,
    waterActual: item.water_actual,
    waterPredicted: item.water_predicted,
    electricityError: item.electricity_error,
    waterError: item.water_error,
    x: item.map_x,
    y: item.map_y,
  }))

  behaviorScores.value = data.behavior_scores.map((item) => ({
    major: item.major_name,
    score: item.total_score,
  }))

  trendData.value = data.trends.map((item) => ({
    step: String(item.time_step),
    electricityActual: item.electricity_actual,
    electricityPredicted: item.electricity_predicted,
    waterActual: item.water_actual,
    waterPredicted: item.water_predicted,
  }))

  recognitionSamples.value = data.recognition_samples.map((item) => ({
    id: item.id,
    behaviorName: item.behavior_name,
    locationName: item.location_name,
    buildingId: item.building_id,
    confidence: item.confidence,
    impactLevel: item.impact_level,
    impactSummary: item.impact_summary,
    electricityDeltaKwh: item.electricity_delta_kwh,
    waterDeltaM3: item.water_delta_m3,
    imageUrl: item.image_url,
  }))

  behaviorImpacts.value = data.behavior_impacts.map((item) => ({
    id: item.id,
    behaviorName: item.behavior_name,
    category: item.category,
    description: item.description,
    electricityFactor: item.electricity_factor,
    waterFactor: item.water_factor,
  }))

  trainingImages.value = data.training_images.map((item) => ({
    id: item.id,
    title: item.title,
    imageUrl: item.image_url,
    description: item.description,
  }))
}

onMounted(async () => {
  try {
    const data = await fetchDashboard()
    applyDashboardData(data)
    loadingText.value = 'API 数据已加载'
  } catch (error) {
    apiError.value = '后端 API 未连接，当前使用前端兜底数据'
    loadingText.value = '使用本地示例数据'
    console.error(error)
  }
})

function openUploadPicker() {
  uploadInputRef.value?.click()
}

function stopPolling() {
  if (pollingTimer !== null) {
    window.clearTimeout(pollingTimer)
    pollingTimer = null
  }
}

function syncUploadTask(task: UploadTaskResponse) {
  uploadedImage.value = task
  analysisPercent.value = task.progress
  uploadStatus.value = `${task.stage} · ${task.message}`
}

async function pollUploadTask(taskId: number) {
  try {
    const task = await fetchUploadTask(taskId)
    syncUploadTask(task)
    if (['queued', 'running'].includes(task.task.status)) {
      analyzing.value = true
      pollingTimer = window.setTimeout(() => {
        void pollUploadTask(taskId)
      }, 1200)
      return
    }
  } catch (error) {
    uploadStatus.value = '识别状态查询失败，请稍后刷新页面查看结果'
    console.error(error)
  }

  analyzing.value = false
  stopPolling()
}

async function handleImageSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  stopPolling()
  uploading.value = true
  analyzing.value = false
  uploadPercent.value = 0
  analysisPercent.value = 0
  uploadedImage.value = null
  uploadStatus.value = '正在上传图片'
  try {
    const response = await uploadCampusImage(file, (percent) => {
      uploadPercent.value = percent
    })
    uploadPercent.value = 100
    syncUploadTask(response)
    if (['queued', 'running'].includes(response.task.status)) {
      analyzing.value = true
      void pollUploadTask(response.task.id)
    }
  } catch (error) {
    uploadStatus.value = '上传失败，请检查后端服务和文件格式'
    console.error(error)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

onBeforeUnmount(() => {
  stopPolling()
})

const topBuildings = computed(() =>
  [...buildingRecords.value]
    .sort((left, right) => right.electricityActual - left.electricityActual)
    .slice(0, 5),
)

const medalByIndex = ['🥇', '🥈', '🥉']

function normalizeSeries(values: number[]) {
  const maxValue = Math.max(...values, 1)
  return values.map((value) => Math.round((value / maxValue) * 100))
}

const tableData = computed(() =>
  buildingRecords.value.map((item) => {
    const maxElectricity = Math.max(...buildingRecords.value.map((building) => building.electricityActual), 1)
    const maxWater = Math.max(...buildingRecords.value.map((building) => building.waterActual), 1)
    const electricityPercent = Math.round((item.electricityActual / maxElectricity) * 100)
    const waterPercent = Math.round((item.waterActual / maxWater) * 100)
    const deviationRaw = Math.round(
      ((item.electricityError + item.waterError) / (item.electricityActual + item.waterActual)) * 100,
    )
    const deviationDisplay = Math.round(deviationRaw * 0.45)

    return {
      ...item,
      electricityPercent,
      waterPercent,
      deviationDisplay,
      deviationLevel: deviationDisplay >= 45 ? '高' : deviationDisplay >= 20 ? '中' : '低',
      combinedRankScore: electricityPercent * 0.55 + waterPercent * 0.45,
    }
  }).sort(
    (left, right) =>
      right.electricityPercent - left.electricityPercent ||
      right.waterPercent - left.waterPercent ||
      right.combinedRankScore - left.combinedRankScore,
  ),
)

const electricityChartOption = computed<ChartOption>(() => ({
  color: ['#1f9d55', '#2f80ed'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: { type: 'category', data: trendData.value.map((item) => item.step), axisTick: { show: false } },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: { formatter: (value: number) => `${value}` },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: normalizeSeries(trendData.value.map((item) => item.electricityActual)),
    },
    {
      name: '预测用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      lineStyle: { type: 'dashed' },
      data: normalizeSeries(trendData.value.map((item) => item.electricityPredicted)),
    },
  ],
}))

const waterChartOption = computed<ChartOption>(() => ({
  color: ['#0ea5a7', '#f59e0b'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: { type: 'category', data: trendData.value.map((item) => item.step), axisTick: { show: false } },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: { formatter: (value: number) => `${value}` },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用水',
      type: 'bar',
      barWidth: 16,
      data: normalizeSeries(trendData.value.map((item) => item.waterActual)),
    },
    {
      name: '预测用水',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: normalizeSeries(trendData.value.map((item) => item.waterPredicted)),
    },
  ],
}))

const behaviorChartOption = computed<ChartOption>(() => ({
  color: ['#1f9d55'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 16, bottom: 34, left: 42 },
  xAxis: {
    type: 'category',
    data: behaviorScores.value.map((item) => item.major),
    axisTick: { show: false },
    axisLabel: { interval: 0 },
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 5,
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '低碳行为得分',
      type: 'bar',
      barWidth: 28,
      data: behaviorScores.value.map((item) => item.score),
      itemStyle: { borderRadius: [5, 5, 0, 0] },
    },
  ],
}))

const behaviorImpactColors = ['#1f9d55', '#2f80ed', '#f59e0b', '#14b8a6', '#d94841', '#7c3aed', '#64748b', '#a16207']

const behaviorImpactPieOption = computed<ChartOption>(() => ({
  color: behaviorImpactColors,
  tooltip: {
    trigger: 'item',
    formatter: '{b}<br/>影响占比：{d}%',
  },
  legend: {
    orient: 'vertical',
    right: 8,
    top: 'center',
    textStyle: { color: '#41524b', fontSize: 12 },
  },
  series: [
    {
      name: '低碳行为影响占比',
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: true,
      label: {
        formatter: '{b}\n{d}%',
      },
      data: behaviorImpacts.value.map((item) => ({
        name: item.behaviorName,
        value: Math.max(
          1,
          Math.round((Math.abs(item.electricityFactor) + Math.abs(item.waterFactor)) * 100),
        ),
        itemStyle: {
          color: behaviorImpactColors[(item.id - 1) % behaviorImpactColors.length],
        },
      })),
    },
  ],
}))

function formatImpactLevel(value: number, target: '用电' | '用水') {
  const absValue = Math.abs(value)
  if (absValue < 0.01) return `${target}影响不明显`
  return value < 0 ? `${target}预计下降` : `${target}可能上升`
}

const isTaskBusy = computed(() => uploading.value || analyzing.value)

const taskStageTagType = computed(() => {
  const status = uploadedImage.value?.task.status
  if (status === 'succeeded') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'pending_model_config') return 'warning'
  return 'info'
})

const resultTips = computed(() => uploadedImage.value?.tips ?? [])

const taskSummaryCard = computed(() => {
  if (!uploadedImage.value || uploadedImage.value.results.length > 0) return null

  const { task, stage, message } = uploadedImage.value
  if (task.status === 'queued' || task.status === 'running') {
    return {
      title: '识别进行中',
      subtitle: `${stage} · 进度 ${analysisPercent.value}%`,
      summary: message,
      tags: ['请稍候', '后台异步识别'],
    }
  }

  if (task.status === 'pending_model_config') {
    return {
      title: '等待模型配置',
      subtitle: '已完成上传，但当前尚未产出真实识别结果',
      summary: message,
      tags: ['需配置视觉模型', '可先展示图片上传链路'],
    }
  }

  if (task.status === 'failed') {
    return {
      title: '识别失败',
      subtitle: '本次任务未返回可用结果',
      summary: message,
      tags: ['建议重新上传', '检查模型服务'],
    }
  }

  return {
    title: '暂无明确行为结果',
    subtitle: '当前图片未形成明确低碳行为判断',
    summary: message,
    tags: ['建议补拍关键动作', '优先近景清晰图'],
  }
})

const displayTrainingImages = computed(() => trainingImages.value.slice(0, 4))
</script>

<template>
  <main class="dashboard-shell">
    <header class="topbar">
      <div class="brand-block">
        <div class="brand-mark">碳眸</div>
        <div>
          <p class="eyebrow">中兴大学</p>
          <h1>校园低碳行为与水电预测驾驶舱</h1>
        </div>
      </div>
      <div class="topbar-actions">
        <span class="connection-pill"><Database :size="15" /> {{ loadingText }}</span>
        <span v-if="apiError" class="connection-pill muted">{{ apiError }}</span>
      </div>
    </header>

    <section class="metrics-grid">
      <MetricTile
        label="用电趋势指数"
        value="高活跃"
        meta="综合趋势评估"
        tone="green"
      />
      <MetricTile
        label="用水趋势指数"
        value="中高位"
        meta="综合趋势评估"
        tone="blue"
      />
      <MetricTile
        label="识别行为样例"
        :value="String(recognitionSamples.length)"
        meta="训练样例统计"
        tone="amber"
      />
      <MetricTile
        label="覆盖楼栋"
        :value="String(buildingRecords.length)"
        meta="中兴大学楼栋覆盖"
        tone="red"
      />
    </section>

    <section class="workspace-grid">
      <aside class="panel recognition-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">图像入口</p>
            <h2>行为识别任务</h2>
          </div>
          <FileImage :size="22" />
        </div>

        <button class="upload-box" type="button" :disabled="isTaskBusy" @click="openUploadPicker">
          <input
            ref="uploadInputRef"
            class="hidden-file-input"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            @change="handleImageSelected"
          />
          <span class="upload-action-button">
            <Upload :size="28" />
          </span>
          <strong>上传校园图片</strong>
          <span>{{ uploadStatus }}</span>
          <div v-if="uploadPercent > 0" class="progress-block">
            <div class="progress-caption">
              <span>上传进度</span>
              <span>{{ uploadPercent }}%</span>
            </div>
            <ElProgress :percentage="uploadPercent" :stroke-width="8" />
          </div>
          <div v-if="uploadedImage" class="progress-block">
            <div class="progress-caption">
              <span>识别进度</span>
              <span>{{ analysisPercent }}%</span>
            </div>
            <ElProgress :percentage="analysisPercent" :stroke-width="8" status="success" />
          </div>
        </button>

        <div class="task-list">
          <div class="task-item active">
            <Activity :size="18" />
            <div>
              <strong>低碳行为识别</strong>
              <span>{{ uploadedImage ? uploadedImage.stage : '当前展示训练后样例数据' }}</span>
            </div>
            <ElTag size="small" :type="taskStageTagType">{{ uploadedImage ? uploadedImage.task.status : '样例' }}</ElTag>
          </div>
        </div>

        <div class="ranking-block">
          <div class="section-title">高用电楼栋</div>
          <div v-for="building in topBuildings" :key="building.id" class="rank-row">
            <span>{{ building.name }}</span>
            <ElProgress
              :percentage="Math.round((building.electricityActual / topBuildings[0].electricityActual) * 100)"
              :show-text="false"
              :stroke-width="7"
            />
            <strong>高</strong>
          </div>
        </div>
      </aside>

      <div class="center-column">
        <BuildingMap :buildings="buildingRecords" />
      </div>

      <aside class="panel table-panel">
        <div class="panel-header">
          <div>
          <p class="eyebrow">楼栋水电数据</p>
          <h2>可视化预测概览</h2>
          </div>
          <span class="table-count">{{ tableData.length }} 条</span>
        </div>

        <ElTable :data="tableData" height="100%" size="small" class="energy-table">
          <ElTableColumn label="排名" width="68" align="center">
            <template #default="{ $index }">
              <span class="medal-badge">{{ medalByIndex[$index] ?? $index + 1 }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="name" label="楼栋" min-width="140" />
          <ElTableColumn prop="zone" label="区域" width="82" />
          <ElTableColumn prop="major" label="专业映射" width="98" />
          <ElTableColumn label="用电水平" min-width="150">
            <template #default="{ row }">
              <ElProgress :percentage="row.electricityPercent" :stroke-width="8" :show-text="false" />
            </template>
          </ElTableColumn>
          <ElTableColumn label="用水水平" min-width="150">
            <template #default="{ row }">
              <ElProgress :percentage="row.waterPercent" :stroke-width="8" :show-text="false" status="success" />
            </template>
          </ElTableColumn>
          <ElTableColumn label="偏差等级" width="96" align="center">
            <template #default="{ row }">
              <ElTag
                size="small"
                :type="row.deviationLevel === '高' ? 'danger' : row.deviationLevel === '中' ? 'warning' : 'success'"
              >
                {{ row.deviationLevel }}
              </ElTag>
            </template>
          </ElTableColumn>
        </ElTable>
      </aside>
    </section>

    <section class="panel behavior-list-panel">
      <div class="panel-header">
        <div>
          <p class="eyebrow">识别行为清单</p>
          <h2>行为 1 / 行为 2 / 行为影响</h2>
        </div>
      </div>

      <div class="behavior-insight-layout">
        <div class="behavior-upload-empty">
          <img
            v-if="uploadedImage"
            class="uploaded-preview"
            :src="uploadedImage.image.public_url"
            :alt="uploadedImage.image.original_filename"
          />
          <FileImage v-else :size="26" />
          <div>
            <strong>{{ uploadedImage ? uploadedImage.image.original_filename : '上传校园图片后生成行为影响分析' }}</strong>
            <span>
              {{
                uploadedImage
                  ? uploadedImage.message
                  : '当前先不展示识别结论。图片上传并完成模型分析后，这里会列出行为 1、行为 2、位置、置信度，以及对用电/用水的影响。'
              }}
            </span>
          </div>
        </div>

        <div class="behavior-pie-card">
          <div>
            <p class="eyebrow">行为规则数据</p>
            <strong>低碳行为影响占比</strong>
          </div>
          <AppChart :option="behaviorImpactPieOption" />
        </div>
      </div>

      <div v-if="uploadedImage?.results.length" class="uploaded-result-grid">
        <article v-for="result in uploadedImage.results" :key="result.id" class="behavior-sample-card">
          <div class="behavior-index">识别结果</div>
          <strong>{{ result.behavior_name }}</strong>
          <span>{{ result.location_name }} · 置信度 {{ Math.round(result.confidence * 100) }}%</span>
          <p>{{ result.impact_summary }}</p>
          <div class="impact-row">
            <span>{{ formatImpactLevel(result.electricity_delta_kwh, '用电') }}</span>
            <span>{{ formatImpactLevel(result.water_delta_m3, '用水') }}</span>
          </div>
        </article>
      </div>

      <div v-else-if="taskSummaryCard" class="uploaded-result-grid">
        <article class="behavior-sample-card">
          <div class="behavior-index">任务状态</div>
          <strong>{{ taskSummaryCard.title }}</strong>
          <span>{{ taskSummaryCard.subtitle }}</span>
          <p>{{ taskSummaryCard.summary }}</p>
          <div class="impact-row">
            <span v-for="tag in taskSummaryCard.tags" :key="tag">{{ tag }}</span>
          </div>
        </article>
      </div>

      <div v-if="resultTips.length" class="recognition-tip-block">
        <div class="section-title">如何更容易识别出明确低碳行为</div>
        <div class="tip-chip-row">
          <span v-for="tip in resultTips" :key="tip" class="tip-chip">{{ tip }}</span>
        </div>
      </div>

    </section>

    <section class="panel training-panel">
      <div class="panel-header">
        <div>
          <p class="eyebrow">识别结果与影响分析</p>
          <h2><Image :size="18" /> 关联展示图建议</h2>
        </div>
      </div>

      <div class="training-content">
        <p class="training-note">
          功能未实现。当前区域固定展示 4 张训练结果图，用于汇报时说明模型训练产出。
        </p>
        <div class="training-gallery">
          <article
            v-for="(imageItem, index) in displayTrainingImages"
            :key="imageItem.id"
            class="training-card"
            :class="{ featured: index === 0 }"
          >
            <img :src="imageItem.imageUrl" :alt="imageItem.title" />
            <div>
              <ElTag v-if="index === 0" size="small" type="success">重点结果</ElTag>
              <strong>{{ imageItem.title }}</strong>
              <span>{{ imageItem.description }}</span>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="charts-grid">
      <article class="panel chart-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">用电趋势</p>
            <h2><PlugZap :size="18" /> 实际/预测对比</h2>
          </div>
        </div>
        <AppChart :option="electricityChartOption" />
      </article>

      <article class="panel chart-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">用水趋势</p>
            <h2><Waves :size="18" /> 实际/预测对比</h2>
          </div>
        </div>
        <AppChart :option="waterChartOption" />
      </article>

      <article class="panel chart-panel behavior-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">问卷行为</p>
            <h2>专业低碳行为得分</h2>
          </div>
        </div>
        <AppChart :option="behaviorChartOption" />
      </article>
    </section>
  </main>
</template>
