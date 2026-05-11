<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  Activity,
  Building2,
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
import { fetchDashboard } from './api/dashboardApi'
import type { DashboardApiResponse } from './api/dashboardApi'
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
import { formatCompact, formatNumber } from './utils/format'
import type { ChartOption } from './types/echarts'

const loadingText = ref('正在连接后端 API')
const apiError = ref('')

// 这些 ref 是页面真正使用的数据源。
// 默认先放入本地兜底数据，避免后端没启动时页面空白。
// 如果 API 请求成功，onMounted 里会用数据库返回的数据覆盖它们。
const buildingRecords = ref<BuildingRecord[]>(fallbackBuildingRecords)
const behaviorScores = ref<BehaviorScore[]>(fallbackBehaviorScores)
const trendData = ref<TrendPoint[]>(fallbackTrendData)
const recognitionSamples = ref<RecognitionSample[]>(fallbackRecognitionSamples)
const behaviorImpacts = ref<BehaviorImpact[]>(fallbackBehaviorImpacts)
const trainingImages = ref<TrainingImage[]>(fallbackTrainingImages)

// 把后端 snake_case 字段转换成前端更常用的 camelCase。
// 这样模板里写 item.electricityActual 会比 item.electricity_actual 更符合前端习惯。
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
    // 页面加载完成后请求后端。
    // 成功：使用 MySQL 数据。
    // 失败：保留 fallback 静态数据，并在顶部提示用户。
    const data = await fetchDashboard()
    applyDashboardData(data)
    loadingText.value = 'API 数据已加载'
  } catch (error) {
    apiError.value = '后端 API 未连接，当前使用前端兜底数据'
    loadingText.value = '使用本地示例数据'
    console.error(error)
  }
})

const totals = computed(() => {
  // computed 是 Vue 的“计算属性”。
  // 这里根据楼栋数组实时计算顶部四张指标卡。
  const electricityActual = buildingRecords.value.reduce((sum, item) => sum + item.electricityActual, 0)
  const electricityPredicted = buildingRecords.value.reduce(
    (sum, item) => sum + item.electricityPredicted,
    0,
  )
  const waterActual = buildingRecords.value.reduce((sum, item) => sum + item.waterActual, 0)
  const waterPredicted = buildingRecords.value.reduce((sum, item) => sum + item.waterPredicted, 0)
  const avgBehavior =
    behaviorScores.value.reduce((sum, item) => sum + item.score, 0) / behaviorScores.value.length

  return {
    electricityActual,
    electricityPredicted,
    waterActual,
    waterPredicted,
    avgBehavior,
  }
})

const topBuildings = computed(() =>
  [...buildingRecords.value]
    .sort((left, right) => right.electricityActual - left.electricityActual)
    .slice(0, 5),
)

const tableData = computed(() =>
  // 表格需要额外展示误差百分比，所以在原始楼栋数据上临时补两个字段。
  buildingRecords.value.map((item) => ({
    ...item,
    electricityGapRate: `${Math.round((item.electricityError / item.electricityActual) * 100)}%`,
    waterGapRate: `${Math.round((item.waterError / item.waterActual) * 100)}%`,
  })),
)

const electricityChartOption = computed<ChartOption>(() => ({
  // ECharts 的配置对象。
  // series 里第一条线是实际用电，第二条虚线是预测用电。
  color: ['#1f9d55', '#2f80ed'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: { type: 'category', data: trendData.value.map((item) => item.step), axisTick: { show: false } },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: (value: number) => formatCompact(value) },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: trendData.value.map((item) => item.electricityActual),
    },
    {
      name: '预测用电',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      lineStyle: { type: 'dashed' },
      data: trendData.value.map((item) => item.electricityPredicted),
    },
  ],
}))

const waterChartOption = computed<ChartOption>(() => ({
  // 用水图：柱状图表示实际用水，折线表示预测用水。
  color: ['#0ea5a7', '#f59e0b'],
  tooltip: { trigger: 'axis' },
  grid: { top: 28, right: 18, bottom: 28, left: 56 },
  xAxis: { type: 'category', data: trendData.value.map((item) => item.step), axisTick: { show: false } },
  yAxis: {
    type: 'value',
    axisLabel: { formatter: (value: number) => formatCompact(value) },
    splitLine: { lineStyle: { color: '#e8eee9' } },
  },
  series: [
    {
      name: '实际用水',
      type: 'bar',
      barWidth: 16,
      data: trendData.value.map((item) => item.waterActual),
    },
    {
      name: '预测用水',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      data: trendData.value.map((item) => item.waterPredicted),
    },
  ],
}))

const behaviorChartOption = computed<ChartOption>(() => ({
  // 行为得分图：展示不同专业的低碳行为问卷得分，满分按 5 分处理。
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
</script>

<template>
  <main class="dashboard-shell">
    <header class="topbar">
      <div class="brand-block">
        <div class="brand-mark">碳眸</div>
        <div>
          <p class="eyebrow">上海电机学院临港校区</p>
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
        label="实际用电总量"
        :value="`${formatCompact(totals.electricityActual)} kWh`"
        :meta="`预测 ${formatCompact(totals.electricityPredicted)} kWh`"
        tone="green"
      />
      <MetricTile
        label="实际用水总量"
        :value="`${formatCompact(totals.waterActual)} m³`"
        :meta="`预测 ${formatCompact(totals.waterPredicted)} m³`"
        tone="blue"
      />
      <MetricTile
        label="识别行为样例"
        :value="String(recognitionSamples.length)"
        meta="来自数据库 recognition_samples"
        tone="amber"
      />
      <MetricTile
        label="覆盖楼栋"
        :value="String(buildingRecords.length)"
        meta="按数据库预测结果统计"
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

        <div class="upload-box">
          <Upload :size="28" />
          <strong>上传校园图片</strong>
          <span>这里预留图片上传入口，后续接入模型后把识别结果写入数据库。</span>
        </div>

        <div class="task-list">
          <div class="task-item active">
            <Activity :size="18" />
            <div>
              <strong>低碳行为识别</strong>
              <span>当前展示训练后样例数据</span>
            </div>
            <ElTag size="small" type="success">样例</ElTag>
          </div>
          <div class="task-item">
            <Building2 :size="18" />
            <div>
              <strong>楼栋归属判断</strong>
              <span>当前按样例数据关联楼栋</span>
            </div>
            <ElTag size="small" type="warning">预留</ElTag>
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
            <strong>{{ formatCompact(building.electricityActual) }}</strong>
          </div>
        </div>
      </aside>

      <div class="center-column">
        <BuildingMap :buildings="buildingRecords" />

        <section class="panel training-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">训练结果与影响分析</p>
              <h2><Image :size="18" /> 校园图片识别预留区</h2>
            </div>
          </div>

          <div class="training-content">
            <div class="upload-inline">
              <Upload :size="22" />
              <div>
                <strong>上传校园图片后显示识别结果</strong>
                <span>后续模型会输出行为、地点、置信度，并评估对用电/用水的影响。</span>
              </div>
            </div>

            <div class="training-gallery">
              <article v-for="imageItem in trainingImages" :key="imageItem.id" class="training-card">
                <img :src="imageItem.imageUrl" :alt="imageItem.title" />
                <div>
                  <strong>{{ imageItem.title }}</strong>
                  <span>{{ imageItem.description }}</span>
                </div>
              </article>
            </div>
          </div>
        </section>
      </div>

      <aside class="panel table-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">楼栋水电数据</p>
            <h2>预测结果表</h2>
          </div>
          <span class="table-count">{{ tableData.length }} 条</span>
        </div>

        <ElTable :data="tableData" height="440" size="small" class="energy-table">
          <ElTableColumn prop="name" label="楼栋" min-width="128" fixed />
          <ElTableColumn prop="zone" label="区域" width="82" />
          <ElTableColumn prop="major" label="专业映射" width="98" />
          <ElTableColumn label="用电" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.electricityActual) }}</template>
          </ElTableColumn>
          <ElTableColumn label="预测用电" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.electricityPredicted) }}</template>
          </ElTableColumn>
          <ElTableColumn prop="electricityGapRate" label="电误差" width="84" align="right" />
          <ElTableColumn label="用水" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.waterActual) }}</template>
          </ElTableColumn>
          <ElTableColumn label="预测用水" width="112" align="right">
            <template #default="{ row }">{{ formatNumber(row.waterPredicted) }}</template>
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

      <div class="behavior-upload-empty">
        <FileImage :size="26" />
        <div>
          <strong>上传校园图片后生成行为影响分析</strong>
          <span>
            当前先不展示识别结论。图片上传并完成模型分析后，这里会列出行为 1、行为 2、位置、置信度，以及对用电/用水的影响。
          </span>
        </div>
      </div>

      <div class="eco-tip-grid">
        <article v-for="impact in behaviorImpacts" :key="`impact-${impact.id}`" class="impact-rule-card">
          <ElTag size="small" :type="impact.category === '用电' ? 'success' : 'info'">
            环保提示 · {{ impact.category }}
          </ElTag>
          <strong>{{ impact.behaviorName }}</strong>
          <span>{{ impact.description }}</span>
        </article>
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
